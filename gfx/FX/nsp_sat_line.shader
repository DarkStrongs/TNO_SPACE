# =============================================================================
# NSP r63 选中卫星的轨道线（与 nsp_sat_bt 同一张数据贴图，只用 R 通道），0.25 s 淡入
# 贴图 480x270（GUI scale = 1），由 work/r61/sat_data.py 生成：
#   R = 抗锯齿轨道线；G + A 低 7 位 = 轨道相位 θ（15 位）；A >= 128 = 有效像素；B = 卫星轨迹带径向衰减
#   像素 (0,0)：R = 初相，G = 周期（秒），B = 卫星半长 eps*20000
# 卫星位置 t = frac(Time / 周期 + 初相)，在 |θ - t| 与径向衰减组成的圆点内画白芯 + 青色辉光。
# 远侧被行星遮挡的轨道段贴图里本来就没有 → 卫星经过时自然消失。
# 时间轴同 nsp_focus_bt：启用瞬间 AnimationTime 刷新，0.7..1.1 s 淡入；禁用态全透明。
# Point 采样：数据贴图不能插值。
# =============================================================================
Includes = {
	"buttonstate.fxh"
}

PixelShader =
{
	Samplers =
	{
		MapTexture =
		{
			Index = 0
			MagFilter = "Point"
			MinFilter = "Point"
			MipFilter = "None"
			AddressU = "Clamp"
			AddressV = "Clamp"
		}
	}
}

VertexStruct VS_OUTPUT
{
	float4  vPosition : PDX_POSITION;
	float2  vTexCoord : TEXCOORD0;
};

VertexShader =
{
	MainCode VertexShader
	[[
		VS_OUTPUT main(const VS_INPUT v )
		{
			VS_OUTPUT Out;
			Out.vPosition  = mul( WorldViewProjectionMatrix, float4( v.vPosition.xyz, 1 ) );
			Out.vTexCoord = v.vTexCoord;
			return Out;
		}
	]]
}

PixelShader =
{
	MainCode PixelShaderNSPSat
	[[
		float4 main( VS_OUTPUT v ) : PDX_COLOR
		{
			float4 c = tex2D( MapTexture, v.vTexCoord );
			if ( c.a < 0.49 ) return float4( 0.0, 0.0, 0.0, 0.0 );
			float dT = Time - AnimationTime;
			float okA = ( AnimationTime > 0.001 && dT >= 0.0 && dT < 120.0 ) ? 1.0 : 0.0;
			float fa = okA > 0.5 ? saturate( dT / 0.25 ) : 1.0;
			// 选中轨道：线稍亮，带一点呼吸
			float pulse = 0.85 + 0.15 * sin( Time * 2.5 );
			float3 teal = float3( 0.455, 0.890, 0.871 );
			return float4( teal, saturate( c.r * 0.95 * pulse ) * fa );
		}
	]]
}

PixelShader =
{
	MainCode PixelShaderNSPHidden
	[[
		float4 main( VS_OUTPUT v ) : PDX_COLOR
		{
			return float4( 0.0, 0.0, 0.0, 0.0 );
		}
	]]
}

BlendState BlendState
{
	BlendEnable = yes
	SourceBlend = "src_alpha"
	DestBlend = "inv_src_alpha"
}

Effect Up
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderNSPSat"
}
Effect Down
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderNSPSat"
}
Effect Disable
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderNSPHidden"
}
Effect Over
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderNSPSat"
}
