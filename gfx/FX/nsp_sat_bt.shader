# =============================================================================
# NSP r61 卫星轨道（行星聚焦视图 / 月球视图）：数据贴图 + 实时运动
# r64：卫星改为像素小图（太阳能板 + 本体），按沿轨/横向坐标采样图集，见 work/r64/sat_data.py
# r63：本 shader 只画卫星；轨道线改由 nsp_sat_line.shader（点右侧图标选中时才显示）
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
			float4 P = tex2D( MapTexture, float2( 0.5 / 480.0, 0.5 / 270.0 ) );
			float period = max( P.g * 255.0, 1.0 );
			float circ = P.b * 255.0 * 8.0;                       // r64：轨道周长（px）
			float th = ( floor( c.g * 255.0 + 0.5 ) * 128.0 + floor( c.a * 255.0 + 0.5 ) - 128.0 ) / 32768.0;
			float t = frac( Time / period + P.r );
			float along = ( frac( th - t + 0.5 ) - 0.5 ) * circ;     // 沿轨距离（px，带符号）
			float across = ( c.b * 255.0 - 128.0 ) / 20.0;            // 横向偏移（px，带符号）
			float3 teal = float3( 0.84, 0.86, 0.89 );   // r74：去掉青色光晕，改为微弱中性反光
			float glow = saturate( 1.0 - sqrt( ( along / 8.0 ) * ( along / 8.0 ) + ( across / 4.0 ) * ( across / 4.0 ) ) ) * 0.12;
			// r74g：卫星图 25x11（图集在贴图 (2,1)，含 1px 透明边），手动双线性采样（预乘 alpha）→ 旋转时边缘平滑
			float pu = 2.0 + 12.5 + along - 0.5;
			float pv = 1.0 + 5.5 + across - 0.5;
			float inS = ( pu >= 1.5 && pu < 26.5 && pv >= 0.5 && pv < 11.5 ) ? 1.0 : 0.0;
			float x0 = floor( pu ); float y0 = floor( pv );
			float fx = pu - x0; float fy = pv - y0;
			float xa = clamp( x0, 2.0, 26.0 ); float xb = clamp( x0 + 1.0, 2.0, 26.0 );
			float ya = clamp( y0, 1.0, 11.0 ); float yb = clamp( y0 + 1.0, 1.0, 11.0 );
			float4 S00 = tex2D( MapTexture, float2( ( xa + 0.5 ) / 480.0, ( ya + 0.5 ) / 270.0 ) );
			float4 S10 = tex2D( MapTexture, float2( ( xb + 0.5 ) / 480.0, ( ya + 0.5 ) / 270.0 ) );
			float4 S01 = tex2D( MapTexture, float2( ( xa + 0.5 ) / 480.0, ( yb + 0.5 ) / 270.0 ) );
			float4 S11 = tex2D( MapTexture, float2( ( xb + 0.5 ) / 480.0, ( yb + 0.5 ) / 270.0 ) );
			float a00 = saturate( S00.a * 2.55 ) * ( 1.0 - fx ) * ( 1.0 - fy );
			float a10 = saturate( S10.a * 2.55 ) * fx * ( 1.0 - fy );
			float a01 = saturate( S01.a * 2.55 ) * ( 1.0 - fx ) * fy;
			float a11 = saturate( S11.a * 2.55 ) * fx * fy;
			float sa0 = a00 + a10 + a01 + a11;
			float3 sc = ( S00.rgb * a00 + S10.rgb * a10 + S01.rgb * a01 + S11.rgb * a11 ) / max( sa0, 0.0001 );
			float sa = sa0 * inS;
			float3 col = lerp( teal, sc, sa );
			float a = max( glow, sa );

			float dT = Time - AnimationTime;
			float okA = ( AnimationTime > 0.001 && dT >= 0.0 && dT < 120.0 ) ? 1.0 : 0.0;
			float fa = okA > 0.5 ? saturate( ( dT - 0.7 ) / 0.4 ) : 1.0;
			return float4( col, a * fa );
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
