import torch
import math
from typing import Union, Sequence, Tuple

_DimsArg = Union[
    int,
    type(Ellipsis),               # 允许单独的 ...
    Sequence[Union[int, type(Ellipsis)]]
]

def _normalize_and_detect_ellipsis(
    dims: _DimsArg,
    ndim: int
) -> Tuple[Tuple[Union[int, type(Ellipsis)], ...], bool]:
    """
    标准化 dims，支持：
      - 单个 int
      - 序列 of int 或 Ellipsis
      - 直接传入 Ellipsis
    返回 (标准化后的 tuple，是否含有 Ellipsis)
    """
    # 直接传入 Ellipsis
    if dims is Ellipsis:
        return (Ellipsis,), True
    # 单个 int
    if isinstance(dims, int):
        d = dims if dims >= 0 else ndim + dims
        return (d,), False

    # 序列
    lst = list(dims)
    has_ellipsis = any(d is Ellipsis for d in lst)
    normalized = []
    for d in lst:
        if d is Ellipsis:
            normalized.append(Ellipsis)
        elif isinstance(d, int):
            normalized.append(d if d >= 0 else ndim + d)
        else:
            raise TypeError(f"维度索引只能是 int 或 Ellipsis，当前：{d!r}")
    return tuple(normalized), has_ellipsis

def _resolve_ellipsis(
    raw: Tuple[Union[int, type(Ellipsis)], ...],
    other: Tuple[int, ...],
    ndim: int
) -> Tuple[int, ...]:
    """
    把 raw 中的 Ellipsis 展开为 “除 raw 中已有 int 及 other 外的所有维度”。
    """
    if raw.count(Ellipsis) > 1:
        raise ValueError("只能出现一个 Ellipsis (…)")
    specified = [d for d in raw if d is not Ellipsis]
    remaining = [i for i in range(ndim) if i not in specified and i not in other]
    out = []
    for d in raw:
        if d is Ellipsis:
            out.extend(remaining)
        else:
            out.append(d)
    return tuple(out)

def _parse_dims(
    inDim: _DimsArg,
    outDim: _DimsArg,
    ndim: int
) -> Tuple[Tuple[int, ...], Tuple[int, ...]]:
    """
    解析并返回 (inDims, outDims)，支持其中一侧使用 Ellipsis。
    抛错情况：
      - 两侧同时出现 Ellipsis
      - 最终 inDims ∪ outDims != 全部维度
      - 有重复维度
    """
    ind_raw, ind_has_elli = _normalize_and_detect_ellipsis(inDim, ndim)
    out_raw, out_has_elli = _normalize_and_detect_ellipsis(outDim, ndim)

    if ind_has_elli and out_has_elli:
        raise ValueError("inDim 和 outDim 不能同时包含 Ellipsis (…)")

    if ind_has_elli:
        # 先把 out_raw 中的非 Ellipsis 值取出，供展开用
        out_fixed = tuple(d for d in out_raw if isinstance(d, int))
        inDims = _resolve_ellipsis(ind_raw, out_fixed, ndim)
        outDims = out_fixed
    elif out_has_elli:
        ind_fixed = tuple(d for d in ind_raw if isinstance(d, int))
        outDims = _resolve_ellipsis(out_raw, ind_fixed, ndim)
        inDims = ind_fixed
    else:
        inDims = tuple(ind_raw)
        outDims = tuple(out_raw)

    # 完整性与无重检查
    all_dims = set(inDims) | set(outDims)
    if len(all_dims) != ndim:
        raise ValueError(
            f"inDim ∪ outDim 必须覆盖全部维度且不重复；"
            f"共覆盖 {len(all_dims)} 维，但张量维度为 {ndim}"
        )
    return inDims, outDims

def flatten_to_2d(
    x: torch.Tensor,
    inDim: _DimsArg,
    outDim: _DimsArg,
) -> Tuple[torch.Tensor, Tuple[int, ...]]:
    """
    将 x 的 inDim 组维度 flatten 到第0 维，outDim 组维度 flatten 到第1 维，
    返回 2D Tensor 和原始 shape。
    """
    ndim = x.dim()
    inDims, outDims = _parse_dims(inDim, outDim, ndim)

    # permute 到 [*outDims, *inDims]
    x_perm = x.permute(*outDims,*inDims)

    # 计算 flatten 后的大小
    I = torch.prod(torch.tensor([x.size(d) for d in inDims])).item()
    O = torch.prod(torch.tensor([x.size(d) for d in outDims])).item()

    return x_perm.reshape(O, I)

def unflatten_from_2d(
    y: torch.Tensor,
    inDim: _DimsArg,
    outDim: _DimsArg,
    orig_shape: Tuple[int, ...],
) -> torch.Tensor:
    """
    将 flatten_to_2d 的输出逆变换回原始形状张量。
    """
    ndim = len(orig_shape)
    inDims, outDims = _parse_dims(inDim, outDim, ndim)

    # 先 reshape 到 [*outDims_sizes, *inDims_sizes]
    ind_sizes = [orig_shape[d] for d in inDims]
    out_sizes = [orig_shape[d] for d in outDims]
    x_perm = y.reshape(*out_sizes, *ind_sizes)

    # 再逆 perm 回原始顺序
    reverse = [0] * ndim
    for new_pos, old_dim in enumerate((*outDims,*inDims)):
        reverse[old_dim] = new_pos

    return x_perm.permute(*reverse)

def glassInit_(weight:torch.Tensor,inDim=...,outDim=0,gain=None,zeroMean=True):
    with torch.no_grad():
        weight.copy_(glassInit(weight,inDim,outDim,gain,zeroMean))


#大多数时候不需要传入外部gain(默认为None)如果传入外部gain则内部gain不生效.
#输入元素数小于输出元素数且关闭稀疏时内部gain为1. 否则内部gain为sqrt(输出元素数/输入元素数)
#需根据矩阵各维度的作用填写inDim和outDim,最终加在一起的要填到inDim,输出时仍然分离的要填到outDim
#举例来说卷积层的inChannel维度和kernels维度要填到inDim里,outChannel维度要填到outDim里
#转置卷积要根据设定参数后的具体行为决定kernels维度要填到哪里,可以先写道inDim中尝试
#如果zeroMean为False,返回矩阵将没有小于零的值,并且是插值矩阵.否则,返回矩阵将对插值矩阵逐元素随机取反.  
#如果输入元素数大于输出元素数或关闭稀疏,矩阵实现线性插值,否则是插0插值.两种插值均为循环边界条件.  
#返回矩阵的维度、尺寸与输入矩阵相同
def glassInit(weight:torch.Tensor,inDim=...,outDim=0,gain=None,zeroMean=True,sparse=True):
    with torch.no_grad():
        tensor2d=flatten_to_2d(weight,inDim,outDim)
        if tensor2d.size(0)>tensor2d.size(1):
            TFlag=True
            M=tensor2d.T
            if gain is None:
                if sparse:
                    gain=math.sqrt(tensor2d.size(0)/tensor2d.size(1))
                else:
                    gain=1
        else:
            TFlag=False
            M=tensor2d
            if gain is None:
                gain=math.sqrt(tensor2d.size(0)/tensor2d.size(1))
        #M矩阵第一维度为短边（行数），第二维度为长边（列数）
        si=M.size(0)
        so=M.size(1)
        eye=torch.eye(si,device=M.device,dtype=M.dtype)
        #eye=torch.diag(torch.randint(0,2,[si],device=M.device,dtype=M.dtype)*2-1) 
        eye3=torch.tile(eye,(1,3))
        #so3=math.ceil((si*3-1)*(((so-((so-si)/(si-1)))-si)/(si-1))+si*3+2)
        so3=math.ceil(so*3-(so/si)+1)
        o3=torch.nn.functional.interpolate(eye3.unsqueeze(0),so3,mode="linear",align_corners=True)
        o=o3.squeeze(0)[:,(so3-so)//2:(so3+so)//2]
        
        
        if TFlag:
            output2d=o.T
            if sparse:
                #下面两行会存在因插值正好平分而连续两个1的情况(其中一个是多余的)
                #output2d-=output2d.amax(dim=1,keepdim=True)
                #output2d=output2d.sign()+1
            
                #因此采用下面这段代码,在单位矩阵中均匀插0
                output2d=torch.zeros_like(output2d)
            
                row_pos = ((torch.arange(si, device=output2d.device) * output2d.size(0)) / si).round().int()   # shape (H,)
                col_pos = ((torch.arange(si, device=output2d.device) * output2d.size(1)) / si).round().int()   # shape (W,)

                row_idx = row_pos.unsqueeze(1).expand(si, si).reshape(-1)
                col_idx = col_pos.unsqueeze(0).expand(si, si).reshape(-1)

                output2d[row_idx, col_idx] = eye.reshape(-1)
        else:
            output2d=o
            
    
        output2d=output2d.sqrt()*gain
        if zeroMean:
            output2d*=(torch.randint_like(output2d,0,2)*2-1)
        output=unflatten_from_2d(output2d,inDim,outDim,weight.shape)
        return output


if __name__ == '__main__':
    a=torch.empty((3,6))
    ao=glassInit(a)
    print(ao)
    print(ao.sum(dim=0))
    print(ao.sum(dim=1))
    b=torch.empty((7,3))
    bo=glassInit(b)
    print(bo)
    print(bo.sum(dim=0))
    print(bo.sum(dim=1))
    
    b=torch.empty((9,3))
    bo=glassInit(b)
    print(bo)
    print(bo.sum(dim=0))
    print(bo.sum(dim=1))
    
    b=torch.empty((8,4))
    bo=glassInit(b)
    print(bo)
    print(bo.sum(dim=0))
    print(bo.sum(dim=1))
    
    b=torch.empty((12,4))
    bo=glassInit(b)
    print(bo)
    print(bo.sum(dim=0))
    print(bo.sum(dim=1))

    b=torch.empty((20,5))
    bo=glassInit(b)
    print(bo)
    print(bo.sum(dim=0))
    print(bo.sum(dim=1))
    
    b=torch.empty((10,2))
    glassInit_(b)
    print(b)
    print(b.sum(dim=0))
    print(b.sum(dim=1))
    
    input=torch.randn((100,2048))
    linear=torch.nn.Linear(512,2048)
    linear2=torch.nn.Linear(2048,512)
    with torch.no_grad():
        glassInit_(linear.weight)
        glassInit_(linear2.weight)
        linear.bias*=0
        output=linear(linear2(input))
        print("std:")
        print(output.std())
        
    # 原始张量
    x = torch.randn(1,2,3,4,5,8,7,45)   # shape = (2,3,4,5)
    # 比如想把 dim (0,2) 拼到第一维（合并成 2*4=8），把 dim (1,3) 拼到第二维（合并成 3*5=15）
    mat = flatten_to_2d(x, inDim=(0,1,5,7), outDim=(6,2,4,3))
    print(mat.shape)  # torch.Size([8, 15])

    # 逆变换
    x_rec = unflatten_from_2d(mat, inDim=(0,1,5,7), outDim=(6,2,4,3), orig_shape=x.shape)
    print(x_rec.shape)            # torch.Size([2,3,4,5])
    print(torch.allclose(x, x_rec))  # True

        


