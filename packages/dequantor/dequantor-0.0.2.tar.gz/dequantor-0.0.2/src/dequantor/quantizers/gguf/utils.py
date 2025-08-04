# Copyright 2025 The HuggingFace Team and City96. All rights reserved.
# #
# # Licensed under the Apache License, Version 2.0 (the "License");
# # you may not use this file except in compliance with the License.
# # You may obtain a copy of the License at
# #
# #     http://www.apache.org/licenses/LICENSE-2.0
# #
# # Unless required by applicable law or agreed to in writing, software
# # distributed under the License is distributed on an "AS IS" BASIS,
# # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# # See the License for the specific language governing permissions and
# # limitations under the License.


from gguf_connector.reader import GGMLQuantizationType, GGML_QUANT_SIZES

# import gguf
import inspect
from contextlib import nullcontext
import torch
import torch.nn as nn

from ...utils import is_accelerate_available


if is_accelerate_available():
    import accelerate
    from accelerate import init_empty_weights
    from accelerate.hooks import add_hook_to_module, remove_hook_from_module


# Copied from diffusers.quantizers.bitsandbytes.utils._create_accelerate_new_hook
def _create_accelerate_new_hook(old_hook):
    r"""
    Creates a new hook based on the old hook. Use it only if you know what you are doing ! This method is a copy of:
    https://github.com/huggingface/peft/blob/748f7968f3a31ec06a1c2b0328993319ad9a150a/src/peft/utils/other.py#L245 with
    some changes
    """
    old_hook_cls = getattr(accelerate.hooks, old_hook.__class__.__name__)
    old_hook_attr = old_hook.__dict__
    filtered_old_hook_attr = {}
    old_hook_init_signature = inspect.signature(old_hook_cls.__init__)
    for k in old_hook_attr.keys():
        if k in old_hook_init_signature.parameters:
            filtered_old_hook_attr[k] = old_hook_attr[k]
    new_hook = old_hook_cls(**filtered_old_hook_attr)
    return new_hook


def _replace_with_gguf_linear(model, compute_dtype, state_dict, prefix="", modules_to_not_convert=[]):
    def _should_convert_to_gguf(state_dict, prefix):
        weight_key = prefix + "weight"
        return weight_key in state_dict and isinstance(state_dict[weight_key], GGUFParameter)

    has_children = list(model.children())
    if not has_children:
        return

    for name, module in model.named_children():
        module_prefix = prefix + name + "."
        _replace_with_gguf_linear(module, compute_dtype, state_dict, module_prefix, modules_to_not_convert)

        if (
            isinstance(module, nn.Linear)
            and _should_convert_to_gguf(state_dict, module_prefix)
            and name not in modules_to_not_convert
        ):
            ctx = init_empty_weights if is_accelerate_available() else nullcontext
            with ctx():
                model._modules[name] = GGUFLinear(
                    module.in_features,
                    module.out_features,
                    module.bias is not None,
                    compute_dtype=compute_dtype,
                )
            model._modules[name].source_cls = type(module)
            # Force requires_grad to False to avoid unexpected errors
            model._modules[name].requires_grad_(False)

    return model


def _dequantize_gguf_and_restore_linear(model, modules_to_not_convert=[]):
    for name, module in model.named_children():
        if isinstance(module, GGUFLinear) and name not in modules_to_not_convert:
            device = module.weight.device
            bias = getattr(module, "bias", None)

            ctx = init_empty_weights if is_accelerate_available() else nullcontext
            with ctx():
                new_module = nn.Linear(
                    module.in_features,
                    module.out_features,
                    module.bias is not None,
                    device=device,
                )
            new_module.weight = nn.Parameter(dequantize_gguf_tensor(module.weight))
            if bias is not None:
                new_module.bias = bias

            # Create a new hook and attach it in case we use accelerate
            if hasattr(module, "_hf_hook"):
                old_hook = module._hf_hook
                new_hook = _create_accelerate_new_hook(old_hook)

                remove_hook_from_module(module)
                add_hook_to_module(new_module, new_hook)

            new_module.to(device)
            model._modules[name] = new_module

        has_children = list(module.children())
        if has_children:
            _dequantize_gguf_and_restore_linear(module, modules_to_not_convert)

    return model


# dequantize operations based on torch ports of GGUF dequantize_functions
# from City96
# more info: https://github.com/city96/ComfyUI-GGUF/blob/main/dequant.py


QK_K = 256
K_SCALE_SIZE = 12


def to_uint32(x):
    x = x.view(torch.uint8).to(torch.int32)
    return (x[:, 0] | x[:, 1] << 8 | x[:, 2] << 16 | x[:, 3] << 24).unsqueeze(1)


def split_block_dims(blocks, *args):
    n_max = blocks.shape[1]
    dims = list(args) + [n_max - sum(args)]
    return torch.split(blocks, dims, dim=1)


def get_scale_min(scales):
    n_blocks = scales.shape[0]
    scales = scales.view(torch.uint8)
    scales = scales.reshape((n_blocks, 3, 4))

    d, m, m_d = torch.split(scales, scales.shape[-2] // 3, dim=-2)

    sc = torch.cat([d & 0x3F, (m_d & 0x0F) | ((d >> 2) & 0x30)], dim=-1)
    min = torch.cat([m & 0x3F, (m_d >> 4) | ((m >> 2) & 0x30)], dim=-1)

    return (sc.reshape((n_blocks, 8)), min.reshape((n_blocks, 8)))


def dequantize_blocks_Q8_0(blocks, block_size, type_size, dtype=None):
    d, x = split_block_dims(blocks, 2)
    d = d.view(torch.float16).to(dtype)
    x = x.view(torch.int8)
    return d * x


def dequantize_blocks_Q5_1(blocks, block_size, type_size, dtype=None):
    n_blocks = blocks.shape[0]

    d, m, qh, qs = split_block_dims(blocks, 2, 2, 4)
    d = d.view(torch.float16).to(dtype)
    m = m.view(torch.float16).to(dtype)
    qh = to_uint32(qh)

    qh = qh.reshape((n_blocks, 1)) >> torch.arange(32, device=d.device, dtype=torch.int32).reshape(1, 32)
    ql = qs.reshape((n_blocks, -1, 1, block_size // 2)) >> torch.tensor(
        [0, 4], device=d.device, dtype=torch.uint8
    ).reshape(1, 1, 2, 1)
    qh = (qh & 1).to(torch.uint8)
    ql = (ql & 0x0F).reshape((n_blocks, -1))

    qs = ql | (qh << 4)
    return (d * qs) + m


def dequantize_blocks_Q5_0(blocks, block_size, type_size, dtype=None):
    n_blocks = blocks.shape[0]

    d, qh, qs = split_block_dims(blocks, 2, 4)
    d = d.view(torch.float16).to(dtype)
    qh = to_uint32(qh)

    qh = qh.reshape(n_blocks, 1) >> torch.arange(32, device=d.device, dtype=torch.int32).reshape(1, 32)
    ql = qs.reshape(n_blocks, -1, 1, block_size // 2) >> torch.tensor(
        [0, 4], device=d.device, dtype=torch.uint8
    ).reshape(1, 1, 2, 1)

    qh = (qh & 1).to(torch.uint8)
    ql = (ql & 0x0F).reshape(n_blocks, -1)

    qs = (ql | (qh << 4)).to(torch.int8) - 16
    return d * qs


def dequantize_blocks_Q4_1(blocks, block_size, type_size, dtype=None):
    n_blocks = blocks.shape[0]

    d, m, qs = split_block_dims(blocks, 2, 2)
    d = d.view(torch.float16).to(dtype)
    m = m.view(torch.float16).to(dtype)

    qs = qs.reshape((n_blocks, -1, 1, block_size // 2)) >> torch.tensor(
        [0, 4], device=d.device, dtype=torch.uint8
    ).reshape(1, 1, 2, 1)
    qs = (qs & 0x0F).reshape(n_blocks, -1)

    return (d * qs) + m


def dequantize_blocks_Q4_0(blocks, block_size, type_size, dtype=None):
    n_blocks = blocks.shape[0]

    d, qs = split_block_dims(blocks, 2)
    d = d.view(torch.float16).to(dtype)

    qs = qs.reshape((n_blocks, -1, 1, block_size // 2)) >> torch.tensor(
        [0, 4], device=d.device, dtype=torch.uint8
    ).reshape((1, 1, 2, 1))
    qs = (qs & 0x0F).reshape((n_blocks, -1)).to(torch.int8) - 8
    return d * qs


def dequantize_blocks_Q6_K(blocks, block_size, type_size, dtype=None):
    n_blocks = blocks.shape[0]

    (
        ql,
        qh,
        scales,
        d,
    ) = split_block_dims(blocks, QK_K // 2, QK_K // 4, QK_K // 16)

    scales = scales.view(torch.int8).to(dtype)
    d = d.view(torch.float16).to(dtype)
    d = (d * scales).reshape((n_blocks, QK_K // 16, 1))

    ql = ql.reshape((n_blocks, -1, 1, 64)) >> torch.tensor([0, 4], device=d.device, dtype=torch.uint8).reshape(
        (1, 1, 2, 1)
    )
    ql = (ql & 0x0F).reshape((n_blocks, -1, 32))
    qh = qh.reshape((n_blocks, -1, 1, 32)) >> torch.tensor([0, 2, 4, 6], device=d.device, dtype=torch.uint8).reshape(
        (1, 1, 4, 1)
    )
    qh = (qh & 0x03).reshape((n_blocks, -1, 32))
    q = (ql | (qh << 4)).to(torch.int8) - 32
    q = q.reshape((n_blocks, QK_K // 16, -1))

    return (d * q).reshape((n_blocks, QK_K))


def dequantize_blocks_Q5_K(blocks, block_size, type_size, dtype=None):
    n_blocks = blocks.shape[0]

    d, dmin, scales, qh, qs = split_block_dims(blocks, 2, 2, K_SCALE_SIZE, QK_K // 8)

    d = d.view(torch.float16).to(dtype)
    dmin = dmin.view(torch.float16).to(dtype)

    sc, m = get_scale_min(scales)

    d = (d * sc).reshape((n_blocks, -1, 1))
    dm = (dmin * m).reshape((n_blocks, -1, 1))

    ql = qs.reshape((n_blocks, -1, 1, 32)) >> torch.tensor([0, 4], device=d.device, dtype=torch.uint8).reshape(
        (1, 1, 2, 1)
    )
    qh = qh.reshape((n_blocks, -1, 1, 32)) >> torch.arange(0, 8, device=d.device, dtype=torch.uint8).reshape(
        (1, 1, 8, 1)
    )
    ql = (ql & 0x0F).reshape((n_blocks, -1, 32))
    qh = (qh & 0x01).reshape((n_blocks, -1, 32))
    q = ql | (qh << 4)

    return (d * q - dm).reshape((n_blocks, QK_K))


def dequantize_blocks_Q4_K(blocks, block_size, type_size, dtype=None):
    n_blocks = blocks.shape[0]

    d, dmin, scales, qs = split_block_dims(blocks, 2, 2, K_SCALE_SIZE)
    d = d.view(torch.float16).to(dtype)
    dmin = dmin.view(torch.float16).to(dtype)

    sc, m = get_scale_min(scales)

    d = (d * sc).reshape((n_blocks, -1, 1))
    dm = (dmin * m).reshape((n_blocks, -1, 1))

    qs = qs.reshape((n_blocks, -1, 1, 32)) >> torch.tensor([0, 4], device=d.device, dtype=torch.uint8).reshape(
        (1, 1, 2, 1)
    )
    qs = (qs & 0x0F).reshape((n_blocks, -1, 32))

    return (d * qs - dm).reshape((n_blocks, QK_K))


def dequantize_blocks_Q3_K(blocks, block_size, type_size, dtype=None):
    n_blocks = blocks.shape[0]

    hmask, qs, scales, d = split_block_dims(blocks, QK_K // 8, QK_K // 4, 12)
    d = d.view(torch.float16).to(dtype)

    lscales, hscales = scales[:, :8], scales[:, 8:]
    lscales = lscales.reshape((n_blocks, 1, 8)) >> torch.tensor([0, 4], device=d.device, dtype=torch.uint8).reshape(
        (1, 2, 1)
    )
    lscales = lscales.reshape((n_blocks, 16))
    hscales = hscales.reshape((n_blocks, 1, 4)) >> torch.tensor(
        [0, 2, 4, 6], device=d.device, dtype=torch.uint8
    ).reshape((1, 4, 1))
    hscales = hscales.reshape((n_blocks, 16))
    scales = (lscales & 0x0F) | ((hscales & 0x03) << 4)
    scales = scales.to(torch.int8) - 32

    dl = (d * scales).reshape((n_blocks, 16, 1))

    ql = qs.reshape((n_blocks, -1, 1, 32)) >> torch.tensor([0, 2, 4, 6], device=d.device, dtype=torch.uint8).reshape(
        (1, 1, 4, 1)
    )
    qh = hmask.reshape(n_blocks, -1, 1, 32) >> torch.arange(0, 8, device=d.device, dtype=torch.uint8).reshape(
        (1, 1, 8, 1)
    )
    ql = ql.reshape((n_blocks, 16, QK_K // 16)) & 3
    qh = (qh.reshape((n_blocks, 16, QK_K // 16)) & 1) ^ 1
    q = ql.to(torch.int8) - (qh << 2).to(torch.int8)

    return (dl * q).reshape((n_blocks, QK_K))


def dequantize_blocks_Q2_K(blocks, block_size, type_size, dtype=None):
    n_blocks = blocks.shape[0]

    scales, qs, d, dmin = split_block_dims(blocks, QK_K // 16, QK_K // 4, 2)
    d = d.view(torch.float16).to(dtype)
    dmin = dmin.view(torch.float16).to(dtype)

    # (n_blocks, 16, 1)
    dl = (d * (scales & 0xF)).reshape((n_blocks, QK_K // 16, 1))
    ml = (dmin * (scales >> 4)).reshape((n_blocks, QK_K // 16, 1))

    shift = torch.tensor([0, 2, 4, 6], device=d.device, dtype=torch.uint8).reshape((1, 1, 4, 1))

    qs = (qs.reshape((n_blocks, -1, 1, 32)) >> shift) & 3
    qs = qs.reshape((n_blocks, QK_K // 16, 16))
    qs = dl * qs - ml

    return qs.reshape((n_blocks, -1))


def dequantize_blocks_BF16(blocks, block_size, type_size, dtype=None):
    return (blocks.view(torch.int16).to(torch.int32) << 16).view(torch.float32)


# this part from calcuis (gguf.org)
# more info: https://github.com/calcuis/gguf-connector/blob/main/src/gguf_connector/quant2c.py

# t quant
# 2-bit; runable, experimental/test purpose
def dequantize_blocks_TQ2_0(blocks, block_size, type_size, dtype=None):
    n_blocks = blocks.shape[0]
    qs, d = split_block_dims(blocks, QK_K // 4)
    d = d.view(torch.float16).to(dtype)
    qs = qs.reshape((n_blocks, -1, 1, 32)) >> torch.tensor([0, 2, 4, 6],
        device=d.device, dtype=torch.uint8).reshape((1, 1, 4, 1))
    qs = (qs & 3).reshape((n_blocks, -1)) - 1
    return d * qs

# 1-bit; runable; for test purpose
def dequantize_blocks_TQ1_0(blocks, block_size, type_size, dtype=None):
    n_blocks = blocks.shape[0]
    qs, qh, d = split_block_dims(blocks, (QK_K - 4 * QK_K // 64) // 5, QK_K // 64)
    d = d.view(torch.float16).to(dtype)
    qs0, qs1 = qs[..., :32], qs[..., 32:]
    qs0 = qs0.reshape((n_blocks, -1, 1, 32)) * torch.tensor(
        [1, 3, 9, 27, 81], device=d.device, dtype=torch.uint8
    ).reshape((1, 1, 5, 1))
    qs0 = qs0.reshape((n_blocks, -1))
    qs1 = qs1.reshape((n_blocks, -1, 1, 16)) * torch.tensor(
        [1, 3, 9, 27, 81], device=d.device, dtype=torch.uint8
    ).reshape((1, 1, 5, 1))
    qs1 = qs1.reshape((n_blocks, -1))
    qh = qh.reshape((n_blocks, -1, 1, 4)) * torch.tensor(
        [1, 3, 9, 27], device=d.device, dtype=torch.uint8
    ).reshape((1, 1, 4, 1))
    qh = qh.reshape((n_blocks, -1))
    qs = torch.cat([qs0, qs1, qh], dim=-1)
    qs = ((qs * 3) >> 8) - 1
    return d * qs

# i quant
# 4-bit; w=super_block_scale (iq4_nl)
def dequantize_blocks_IQ4_NL(blocks, block_size, type_size, dtype=None):
    kvalues = torch.tensor(
        [-127, -104, -83, -65, -49, -35, -22, -10, 1, 13, 25, 38, 53, 69, 89, 113],
        dtype=torch.float32, device=blocks.device
    )
    n_blocks = blocks.shape[0]
    d, qs = split_block_dims(blocks, 2)
    d = d.view(torch.float16).to(dtype)
    qs = qs.reshape((n_blocks, -1, 1, block_size // 2)) >> torch.tensor(
        [0, 4], device=blocks.device, dtype=torch.uint8
    ).reshape((1, 1, 2, 1))
    qs = (qs & 15).reshape((n_blocks, -1)).to(torch.int64)
    kvalues = kvalues.view(1, 1, 16)
    qs = qs.unsqueeze(-1)
    qs = torch.gather(kvalues.expand(qs.shape[0], qs.shape[1], 16), 2, qs)
    qs = qs.squeeze(-1).to(dtype)
    return d * qs

# 4-bit; w=super_block_scale (iq4_xs); 4.25 bit/weight
def dequantize_blocks_IQ4_XS(blocks, block_size, type_size, dtype=None):
    kvalues = torch.tensor(
        [-127, -104, -83, -65, -49, -35, -22, -10, 1, 13, 25, 38, 53, 69, 89, 113],
        dtype=torch.float32, device=blocks.device
    )
    n_blocks = blocks.shape[0]
    d, scales_h, scales_l, qs = split_block_dims(blocks, 2, 2, QK_K // 64)
    d = d.view(torch.float16).to(dtype)
    scales_h = scales_h.view(torch.int16)
    scales_l = scales_l.reshape((n_blocks, -1, 1)) >> torch.tensor(
        [0, 4], device=blocks.device, dtype=torch.uint8).reshape((1, 1, 2))
    scales_h = scales_h.reshape((n_blocks, 1, -1)) >> torch.tensor(
        [2 * i for i in range(QK_K // 32)], device=blocks.device, dtype=torch.uint8).reshape((1, -1, 1))
    scales_l = scales_l.reshape((n_blocks, -1)) & 0x0F
    scales_h = scales_h.reshape((n_blocks, -1)) & 0x03
    scales = (scales_l | (scales_h << 4)) - 32
    dl = (d * scales.to(dtype)).reshape((n_blocks, -1, 1))
    shifts_q = torch.tensor([0, 4], device=blocks.device, dtype=torch.uint8).reshape(1, 1, 2, 1)
    qs = qs.reshape((n_blocks, -1, 1, 16)) >> shifts_q
    qs = (qs & 15).reshape((n_blocks, -1, 32)).to(torch.int64)
    kvalues = kvalues.view(1, 1, 1, 16)
    qs = qs.unsqueeze(-1)
    qs = torch.gather(kvalues.expand(qs.shape[0], qs.shape[1], qs.shape[2], 16), 3, qs)
    qs = qs.squeeze(-1).to(dtype)
    return (dl * qs).reshape(n_blocks, -1)

from gguf_connector.quant2b import load_grid_tensor
# 2-bit; w=super_block_scale (iq2_s); 2.5 bit/weight
def dequantize_blocks_IQ2_S(blocks, block_size, type_size, dtype=None):
    grid_shape = (1024, 8)
    grid_map = (0x08, 0x19, 0x2b)
    grid_hex = (
        b"00000200050008000a0011001400160019002000220025002800410044004600"
        b"490050005200550058006100640066006900800082008500880091009400a000"
        b"a500aa0001010401060109011001120115011801210124014001420145014801"
        b"510154015601590160016501680181018401900192019501a101a40100020202"
        b"050208021102140220022a02410244024602490250025502800285028a029402"
        b"a202010404040604090410041204150418042104240426042904400442044504"
        b"48044a0451045404560459046004620465048104840486048904900495049804"
        b"a104a40400050205050508050a05110514051605190520052505280541054405"
        b"46054905500552055505580561056405800582058505880591059405a0050106"
        b"0406060609061006150640064506480651065406600681068406900600080208"
        b"050808081108140816081908200825082a084108440846084908500852085508"
        b"580861086408800885089408aa08010904091009120915091809210940094509"
        b"480951095409600981099009000a110a140a220a280a2a0a500a990a01100410"
        b"0610091010101210151018102110241026104010421045104810511054105610"
        b"59106010621065106810811084108610901095109810a110a410001102110511"
        b"08110a1111111411161119112011221125112811411144114611491150115211"
        b"5511581161116411801182118511881191119411011204120912101215122112"
        b"2412401245125112541281128412901200140214051408141114141416141914"
        b"2014251428144114441446144914501452145514581461146414801482148514"
        b"881491149414a014011504150615091510151215151518152115241540154215"
        b"4515481551155415601581158415901500160516081611161416201641164416"
        b"50168016aa160118041806180918101815181818211840184218451848185118"
        b"541860188118841800190219051908191119141920194119441950196919a219"
        b"041a101a401a561a00200220052008201120142016201920202025202a204120"
        b"4420502052205520642080208a209420aa200121042110211221152121214021"
        b"4221452151215421602181218421902100220a22222228222a22442250228822"
        b"8a22a82201240424062409241024152418242124242440244224452448245124"
        b"5424602481248424902400250525082511251425202541254425502566258025"
        b"0126042610264026592600280528112814284128442850288a28aa2801290429"
        b"102995290a2a222a642a882a8a2a014004400640094010401240154018401a40"
        b"21402440264040404240454048404a4051405440564059406040624065408140"
        b"8440904095409840a140a4400041024105410841114114411641194120412241"
        b"2541414144414641494150415241554158416141644180418241854188419141"
        b"9441a04101420442104212421542184224424042454248425142544260428142"
        b"844200440244054408440a441144144416441944204422442544284441444444"
        b"46444944504452445544584461446444804482448544884491449444a0440145"
        b"0445064509451045124515451845214524454045424545454845514554456045"
        b"6a4581458445904500460246054608461146144620464146444650468046a546"
        b"0148044809481048124815481848214824484048424845484848514854486048"
        b"84489048004902490549084911491449204941494449504980499649014a044a"
        b"104a404a00500250055008501150145016501950205022502550285041504450"
        b"4650495050505250555058506150645080508250855088509150945001510451"
        b"0651095110511251155118512151245140514251455148515151545160518151"
        b"8451905100520552085211521452205241524452505269528052015404540654"
        b"0954105412541554185421542454405442544554485451545454605481548454"
        b"9054005502550555085511551455205541554455505580550156045610562656"
        b"405600580258055808581158145820584158445850585a588058015904591059"
        b"4059005a195a855aa85a01600460066010601260156018602160246040604560"
        b"4860516054606060846090600061026105610861116114612061416144615061"
        b"806199610462106240625662a162006405640864116414642064416444645064"
        b"806401650465106540654a656865926500669466016804681068656898680069"
        b"2a69426aa16a0080028005800880118014801980208025804180448050805280"
        b"5580588061808080858091809480018104810981108112811581188121812481"
        b"408142814581488151815481818184819081a981008205820a82118214824182"
        b"4482508201840484068409841084128415841884218440844284458448845184"
        b"5484608481848484908400850285058508851185148520854185448550858085"
        b"8a85018604861086298640860088058811881488418844885088a28801890489"
        b"40896589228a588a5a8a828aa28a019004900990109012901590189024904090"
        b"4290459048905190549060908190849090900091059111911491419144915091"
        b"5a910192049210924092a6920094029405940894119414942094419444945094"
        b"8094969401950495109540959895a19500964696649601980498109826984098"
        b"a998009949995299909a00a005a00aa014a022a02aa041a044a050a0a2a0aaa0"
        b"40a165a102a20aa222a228a22aa282a288a28aa2a8a201a404a410a440a489a4"
        b"a4a400a519a551a60aa828a8a2a854a986a908aa0aaa20aa22aa28aa88aaaaaa"
    )
    n_blocks = blocks.shape[0]
    d, qs, signs, qh, scales = split_block_dims(blocks, 2, QK_K // 8, QK_K // 8, QK_K // 32)
    d = d.view(torch.float16).to(dtype)
    scales = scales.reshape(n_blocks, -1, 1) >> torch.tensor([0, 4], dtype=torch.uint8, device=d.device).view(1, 1, 2)
    scales = (scales & 15).reshape(n_blocks, -1).to(dtype)
    db = d * (0.5 + scales) * 0.25
    db = db.view(n_blocks, -1, 1, 1)
    # signs = signs.reshape((n_blocks, -1, 1)) >> torch.arange(
    #     [i for i in range(8)], dtype=torch.uint8, device=d.device).reshape((1, 1, 8))
    signs = signs.reshape(n_blocks, -1, 1) >> torch.tensor(
        [i for i in range(8)], device=d.device, dtype=torch.uint8).reshape(1, 1, 8)
    signs = (signs & 1).to(dtype)
    signs = torch.where(signs == 0, 1.0, -1.0)
    signs = signs.view(n_blocks, -1, 2, 8)
    qh = qh.view(n_blocks, -1, 1) >> torch.tensor([0, 2, 4, 6], dtype=torch.uint8, device=d.device).view(1, 1, 4)
    qs = qs.to(torch.int64) | ((qh & 3) << 8).reshape(n_blocks, -1)  # shape: (n_blocks, 64)
    grid = load_grid_tensor(grid_shape, grid_hex, grid_map, device=d.device)  # shape: (1, 1, 1024, 8)
    grid = grid.expand(n_blocks, 1, *grid_shape)                            # shape: (n_blocks, 1, 1024, 8)
    grid = grid.squeeze(1)  # remove 1-channel dimension → (n_blocks, 1024, 8)
    # version 0 #
    # grid = torch.take_along_dim(grid, (qs & 511).reshape((n_blocks, -1, 1, 1)), dim=-2)
    # grid = grid.reshape((n_blocks, -1, 2, 8))
    # version 1 #
    # gathered_grid = torch.gather(grid, dim=1, index=qs.unsqueeze(-1).expand(-1, -1, 4))  # (n_blocks, 64, 4)
    # gathered_grid = gathered_grid.unsqueeze(-1).expand(-1, -1, -1, 8)  # (n_blocks, 64, 4, 8)
    # db = db.expand(-1, 64, 4, 8)  # Match shapes
    # return (db * gathered_grid * signs).reshape(n_blocks, -1)
    # version 2 #
    # n_blocks, n_qs = qs.shape
    # gathered_grid = torch.gather(grid, dim=1, index=qs.unsqueeze(-1).expand(-1, -1, 4))  # (n_blocks, n_qs, 4)
    # gathered_grid = gathered_grid.unsqueeze(-1).expand(-1, -1, -1, 8)  # (n_blocks, n_qs, 4, 8)
    # db = db.expand(-1, n_qs, 4, 8) # adjustment for shapes
    # return (db * gathered_grid.to(dtype) * signs).reshape(n_blocks, -1) # skip grid for test
    return (db * signs).reshape(n_blocks, -1)

ksigns: bytes = (
    b"\x00\x81\x82\x03\x84\x05\x06\x87\x88\x09\x0a\x8b\x0c\x8d\x8e\x0f"
    b"\x90\x11\x12\x93\x14\x95\x96\x17\x18\x99\x9a\x1b\x9c\x1d\x1e\x9f"
    b"\xa0\x21\x22\xa3\x24\xa5\xa6\x27\x28\xa9\xaa\x2b\xac\x2d\x2e\xaf"
    b"\x30\xb1\xb2\x33\xb4\x35\x36\xb7\xb8\x39\x3a\xbb\x3c\xbd\xbe\x3f"
    b"\xc0\x41\x42\xc3\x44\xc5\xc6\x47\x48\xc9\xca\x4b\xcc\x4d\x4e\xcf"
    b"\x50\xd1\xd2\x53\xd4\x55\x56\xd7\xd8\x59\x5a\xdb\x5c\xdd\xde\x5f"
    b"\x60\xe1\xe2\x63\xe4\x65\x66\xe7\xe8\x69\x6a\xeb\x6c\xed\xee\x6f"
    b"\xf0\x71\x72\xf3\x74\xf5\xf6\x77\x78\xf9\xfa\x7b\xfc\x7d\x7e\xff"
)
# 3-bit; w=super_block_scale (iq3_xxs); 3.06 bit/weight
def dequantize_blocks_IQ3_XXS(blocks, block_size, type_size, dtype=None):
    grid_shape = (256, 4)
    grid_map = (0x04, 0x0c, 0x14, 0x1c, 0x24, 0x2c, 0x34, 0x3e)
    grid_hex = (
        b"0000020004001100130017002000220031004200730075000101030110011201"
        b"2101250130013201410154017001000202020402110220022202310233023702"
        b"5102570275020103070310031203250370031304370444045704730475040105"
        b"0705320552053506640610071407160743076107011003101010121021102310"
        b"3010321034104710501000110211111120112211011203121012121221123012"
        b"7212001302132013311346136613011405145014201524154615711505162217"
        b"4017002002201120132020202220262031204220012103210521102112212121"
        b"3021632167217021002202221122172220222222372240225522012310231423"
        b"7023742335245324032527254125742501270327162745270130103012302130"
        b"2330503065307230003102312031313144314631013203321032253252327232"
        b"1133333330344734723400350635223555351436363663363337603704401740"
        b"3540374053405740744120423742404260426642074345430444514464442545"
        b"4345704505471047124730471250415070500051065126515551145232527252"
        b"0253535310542354275472540255315550562457425724604460466064602161"
        b"6161176264623063366344640565526533660367216703700570077010703270"
        b"5270267140711272457252720073157333736073217441740075027524753076"
    )
    n_blocks = blocks.shape[0]
    d, qs, scales = split_block_dims(blocks, 2, QK_K // 4)
    d = d.view(torch.float16).to(dtype)
    scales = to_uint32(scales)
    db = d * (0.5 + (scales >> 28)) * 0.5
    db = db.reshape(n_blocks, -1, 1, 1)
    bit_shifts = torch.tensor([0, 7, 14, 21], device=d.device, dtype=torch.uint8).reshape(1, 1, 4)
    signs = scales.reshape(n_blocks, -1, 1) >> bit_shifts
    # ksigns = torch.frombuffer(ksigns, dtype=torch.uint8).reshape((1, 1, 1, 128)) # runnable but trigger non-writable warning
    signs = signs.reshape(n_blocks, -1, 1) >> torch.tensor(
        [i for i in range(8)], device=d.device, dtype=torch.uint8).reshape(1, 1, 8)
    signs = signs & 1
    sign_shifts = torch.arange(8, device=d.device, dtype=torch.uint8).view(1, 1, 8)
    signs = signs.reshape(n_blocks, -1, 1) >> sign_shifts
    signs = (signs & 1).float()
    signs = torch.where(signs == 0, torch.tensor(1.0, device=d.device), torch.tensor(-1.0, device=d.device))
    signs = signs.reshape(n_blocks, -1, 4, 8)
    qs = qs.reshape(n_blocks, -1, 1, 1)
    grid = load_grid_tensor(grid_shape, grid_hex, grid_map, device=d.device)   # (256, 4)
    grid = grid.expand(n_blocks, 1, *grid_shape)                               # shape: (n_blocks, 1, 256, 4)
    # version 2 (to be reviewed) #
    # grid = grid.unsqueeze(0).expand(n_blocks, -1, -1)       # (n_blocks, 256, 4)
    # qs_exp = qs.unsqueeze(-1).expand(-1, -1, 4)             # (n_blocks, 64, 4)
    # grid = torch.gather(grid, dim=1, index=qs_exp)          # (n_blocks, 64, 4)
    # grid = grid.view(n_blocks, 64, 4, 1).expand(-1, -1, -1, 8) # (n_blocks, 64, 4, 8)
    # version 1 #
    # grid = torch.take_along_dim(grid, qs.reshape((n_blocks, -1, 1, 1)), dim=-2) # dropped option
    # grid = grid.reshape((n_blocks, -1, 4, 8))             # Ensure matching shape
    # assert db.shape == grid.shape == signs.shape, f"{db.shape} != {grid.shape} != {signs.shape}"
    # return (db * grid * signs).reshape((n_blocks, -1))    # skip grid recently for speed test
    return (db * signs).reshape(n_blocks, -1)

# 3-bit; w=super_block_scale (iq3_s); 3.44 bit/weight
def dequantize_blocks_IQ3_S(blocks, block_size, type_size, dtype=None):
    grid_shape = 512, 4
    grid_map = (0x01, 0x03, 0x05, 0x07, 0x09, 0x0b, 0x0d, 0x0f)
    grid_hex = (
        b"0000010002000500070010001100120014001600200021002500330040004200"
        b"4500470051005300600062007100740077000001010102010401100111011501"
        b"2001230127013101350144016101650172010002010205020702100213021602"
        b"2102250230023402420245024702510253027002730203031103150320032203"
        b"3103330336034403500352036703710375030004130417042104240432044004"
        b"4304510470040205040520052205260533054105450547056605730506061106"
        b"1306310652067106000702070407200722072607330750075407001001100210"
        b"0410101011101310151017102010221031103410361054105610611072100011"
        b"0111031106111011141121113011331141115011521170117611001212121512"
        b"1712201224123212401243125512601272120113041307131013131321132713"
        b"3013341341136213701303140514121414143114331442144614501454140115"
        b"1015131521153015321551152016241627164416461601170317101712172117"
        b"3517411762177017002001200320052007201020122014201620212023202720"
        b"3020322041204320452050205220672070207320752000210221102113211721"
        b"2221252131213421422151210122042207222122232230223722412253225722"
        b"7122742200230223052311232223242331233323422350236623012407242024"
        b"2324322435244124722475240425112522253725402553257025002602260726"
        b"2126552661260527112726273027432750270230113013301530173022303130"
        b"3330353042304430473051306330713001310331053114312131233140316031"
        b"7231763100321232203232323432503201331033143321332333273330334133"
        b"4333473355337333033411341634223431345234603464340135103512352535"
        b"3235443556357335163641360137033720372237353700400440124020402440"
        b"2740324041405040704002410741114113412241304135414341514155410142"
        b"0342104215422142334240425742624270420443114313432043224331433543"
        b"0044024424443744404471440545074521456245134634466046104715473047"
        b"4347514702501050145022504050445047505250665074500151035105511251"
        b"2151325172510052115223523052365253520253075310532753445351536553"
        b"7353015404542054325446541255265551555355425602570457225711601360"
        b"1560316033606060006120612761646112623462426255626262706200631463"
        b"2163406325644364626400650365346560650566406611671367007004700770"
        b"2070227036704070547062700271117124714371457101720472107216722172"
        b"3072517202733273357353730174057413742074507422754275027631760077"
    )
    n_blocks = blocks.shape[0]
    d, qs, qh, signs, scales = split_block_dims(blocks, 2, QK_K // 4, QK_K // 32, QK_K // 8)
    d = d.view(torch.float16).to(dtype)
    scales = scales.reshape(n_blocks, -1, 1) >> torch.tensor([0, 4], dtype=torch.uint8, device=d.device).view(1, 1, 2)
    scales = (scales & 15).reshape(n_blocks, -1).to(dtype)
    db = d * (1 + 2 * scales)
    db = db.view(n_blocks, -1, 1, 1)
    signs = signs.view(n_blocks, -1, 1) >> torch.arange(8, dtype=torch.uint8, device=d.device).view(1, 1, 8)
    signs = (signs & 1).to(dtype)
    signs = torch.where(signs == 0, 1.0, -1.0)
    signs = signs.view(n_blocks, -1, 4, 8)
    qh = qh.view(n_blocks, -1, 1) >> torch.arange(8, dtype=torch.uint8, device=d.device).view(1, 1, 8)
    qh = (qh & 1).view(n_blocks, -1).to(torch.int16)
    qs = qs.to(torch.int64) | (qh << 8)  # shape: (n_blocks, 64)
    grid = load_grid_tensor(grid_shape, grid_hex, grid_map, device=d.device)  # shape: (1, 1, 512, 4)
    grid = grid.expand(n_blocks, 1, *grid_shape)                            # shape: (n_blocks, 1, 512, 4)
    grid = grid.squeeze(1)  # remove 1-channel dimension → (n_blocks, 512, 4)
    # version 1 #
    # gathered_grid = torch.gather(grid, dim=1, index=qs.unsqueeze(-1).expand(-1, -1, 4))  # (n_blocks, 64, 4)
    # gathered_grid = gathered_grid.unsqueeze(-1).expand(-1, -1, -1, 8)  # (n_blocks, 64, 4, 8)
    # db = db.expand(-1, 64, 4, 8)  # Match shapes
    # return (db * gathered_grid * signs).reshape(n_blocks, -1)
    # version 2 #
    # n_blocks, n_qs = qs.shape
    # gathered_grid = torch.gather(grid, dim=1, index=qs.unsqueeze(-1).expand(-1, -1, 4))  # (n_blocks, n_qs, 4)
    # gathered_grid = gathered_grid.unsqueeze(-1).expand(-1, -1, -1, 8)  # (n_blocks, n_qs, 4, 8)
    # db = db.expand(-1, n_qs, 4, 8) # adjustment for shapes
    # return (db * gathered_grid.to(dtype) * signs).reshape(n_blocks, -1) # skip grid for test
    return (db * signs).reshape(n_blocks, -1)

GGML_QUANT_SIZES = GGML_QUANT_SIZES
dequantize_functions = {
    GGMLQuantizationType.BF16:dequantize_blocks_BF16,
    GGMLQuantizationType.Q8_0:dequantize_blocks_Q8_0,
    GGMLQuantizationType.Q5_1:dequantize_blocks_Q5_1,
    GGMLQuantizationType.Q5_0:dequantize_blocks_Q5_0,
    GGMLQuantizationType.Q4_1:dequantize_blocks_Q4_1,
    GGMLQuantizationType.Q4_0:dequantize_blocks_Q4_0,
    GGMLQuantizationType.Q6_K:dequantize_blocks_Q6_K,
    GGMLQuantizationType.Q5_K:dequantize_blocks_Q5_K,
    GGMLQuantizationType.Q4_K:dequantize_blocks_Q4_K,
    GGMLQuantizationType.Q3_K:dequantize_blocks_Q3_K,
    GGMLQuantizationType.Q2_K:dequantize_blocks_Q2_K,
    GGMLQuantizationType.TQ2_0:dequantize_blocks_TQ2_0,
    GGMLQuantizationType.TQ1_0:dequantize_blocks_TQ1_0,
    GGMLQuantizationType.IQ4_NL:dequantize_blocks_IQ4_NL,
    GGMLQuantizationType.IQ4_XS:dequantize_blocks_IQ4_XS,
    GGMLQuantizationType.IQ2_S:dequantize_blocks_IQ2_S,
    GGMLQuantizationType.IQ3_XXS:dequantize_blocks_IQ3_XXS,
    GGMLQuantizationType.IQ3_S:dequantize_blocks_IQ3_S,
    }

# GGML_QUANT_SIZES = gguf.GGML_QUANT_SIZES
# dequantize_functions = {
#     gguf.GGMLQuantizationType.BF16: dequantize_blocks_BF16,
#     gguf.GGMLQuantizationType.Q8_0: dequantize_blocks_Q8_0,
#     gguf.GGMLQuantizationType.Q5_1: dequantize_blocks_Q5_1,
#     gguf.GGMLQuantizationType.Q5_0: dequantize_blocks_Q5_0,
#     gguf.GGMLQuantizationType.Q4_1: dequantize_blocks_Q4_1,
#     gguf.GGMLQuantizationType.Q4_0: dequantize_blocks_Q4_0,
#     gguf.GGMLQuantizationType.Q6_K: dequantize_blocks_Q6_K,
#     gguf.GGMLQuantizationType.Q5_K: dequantize_blocks_Q5_K,
#     gguf.GGMLQuantizationType.Q4_K: dequantize_blocks_Q4_K,
#     gguf.GGMLQuantizationType.Q3_K: dequantize_blocks_Q3_K,
#     gguf.GGMLQuantizationType.Q2_K: dequantize_blocks_Q2_K,
# }
SUPPORTED_GGUF_QUANT_TYPES = list(dequantize_functions.keys())


def _quant_shape_from_byte_shape(shape, type_size, block_size):
    return (*shape[:-1], shape[-1] // type_size * block_size)


def dequantize_gguf_tensor(tensor):
    if not hasattr(tensor, "quant_type"):
        return tensor

    quant_type = tensor.quant_type
    dequant_fn = dequantize_functions[quant_type]

    block_size, type_size = GGML_QUANT_SIZES[quant_type]

    tensor = tensor.view(torch.uint8)
    shape = _quant_shape_from_byte_shape(tensor.shape, type_size, block_size)

    n_blocks = tensor.numel() // type_size
    blocks = tensor.reshape((n_blocks, type_size))

    dequant = dequant_fn(blocks, block_size, type_size)
    dequant = dequant.reshape(shape)

    return dequant.as_tensor()


class GGUFParameter(torch.nn.Parameter):
    def __new__(cls, data, requires_grad=False, quant_type=None):
        data = data if data is not None else torch.empty(0)
        self = torch.Tensor._make_subclass(cls, data, requires_grad)
        self.quant_type = quant_type
        block_size, type_size = GGML_QUANT_SIZES[quant_type]
        self.quant_shape = _quant_shape_from_byte_shape(self.shape, type_size, block_size)

        return self

    def as_tensor(self):
        return torch.Tensor._make_subclass(torch.Tensor, self, self.requires_grad)

    @staticmethod
    def _extract_quant_type(args):
        # When converting from original format checkpoints we often use splits, cats etc on tensors
        # this method ensures that the returned tensor type from those operations remains GGUFParameter
        # so that we preserve quant_type information
        for arg in args:
            if isinstance(arg, list) and isinstance(arg[0], GGUFParameter):
                return arg[0].quant_type
            if isinstance(arg, GGUFParameter):
                return arg.quant_type
        return None

    @classmethod
    def __torch_function__(cls, func, types, args=(), kwargs=None):
        if kwargs is None:
            kwargs = {}

        result = super().__torch_function__(func, types, args, kwargs)

        if isinstance(result, torch.Tensor):
            quant_type = cls._extract_quant_type(args)
            return cls(result, quant_type=quant_type)
        # Handle tuples and lists
        elif type(result) in (list, tuple):
            # Preserve the original type (tuple or list)
            quant_type = cls._extract_quant_type(args)
            wrapped = [cls(x, quant_type=quant_type) if isinstance(x, torch.Tensor) else x for x in result]
            return type(result)(wrapped)
        else:
            return result


class GGUFLinear(nn.Linear):
    def __init__(
        self,
        in_features,
        out_features,
        bias=False,
        compute_dtype=None,
        device=None,
    ) -> None:
        super().__init__(in_features, out_features, bias, device)
        self.compute_dtype = compute_dtype

    def forward(self, inputs):
        weight = dequantize_gguf_tensor(self.weight)
        weight = weight.to(self.compute_dtype)
        bias = self.bias.to(self.compute_dtype) if self.bias is not None else None

        output = torch.nn.functional.linear(inputs, weight, bias)
        return output