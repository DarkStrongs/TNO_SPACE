# =============================================================================
# NSP v23（凹凸 + 大气辉光）/ v24 公转 行星聚焦动画（点击进入）
# 元素：iconType + frameAnimatedSpriteType（20 帧，25fps，play_on_show，looping = no）
# 帧序号 = 时间轴：t = 帧/19。0~0.35 背景渐暗；0.3~1 行星从原位飞到地图中央并放大；
# 动画停在最后一帧，之后靠 Time 继续自转。
# 贴图 4800×135：经纬图切 5 条带（每条 940 列，含 2 列补边）+ 参数区 x 4700..4800
#   P0 R=起点x/480 G=起点y/270 B=起始半径/30   P1 R=光照/360 G=自转档 B=辉光
#   P2 R=终点半径/150 G=土星环  P3/P4 = 土星环颜色/透明度（纵向）
# =============================================================================
Includes = {
	"buttonstate.fxh"
	"sprite_animation.fxh"
}

PixelShader =
{
	Samplers =
	{
		MapTexture =
		{
			Index = 0
			MagFilter = "Linear"
			MinFilter = "Linear"
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
	MainCode PixelShaderNSPOrbit
	[[
		float4 main( VS_OUTPUT v ) : PDX_COLOR
		{
			float pi = 3.141592654;
			float NF = 20.0;
			float fx = v.vTexCoord.x * NF;
			float k1 = min( floor( fx ), NF - 1.0 );
			float lx = fx - k1;
			float k2 = floor( Offset.x * NF + 0.5 );
			float t = 0.0;   // 常驻小行星：不暗背景、不放大

			float4 p0 = tex2D( MapTexture, float2( 4710.0 / 4800.0, 0.5 ) );
			float4 p1 = tex2D( MapTexture, float2( 4730.0 / 4800.0, 0.5 ) );
			float4 p2 = tex2D( MapTexture, float2( 4750.0 / 4800.0, 0.5 ) );
			float2 px = float2( lx * 480.0, v.vTexCoord.y * 270.0 );
			// v22 缓动：位置 easeInOutCubic，半径按指数插值（像镜头推近），背景先暗
			float u = saturate( ( t - 0.10 ) / 0.90 );
			float m = u < 0.5 ? 4.0 * u * u * u : 1.0 - pow( -2.0 * u + 2.0, 3.0 ) * 0.5;
			float zs = 0.5 - 0.5 * cos( u * pi );
			// v24 公转：起点 = 当前 Time 的轨道位置（与 nsp_orbit.shader 同一公式）
			float oA = p0.a * 255.0;
			float oB = p1.a * 100.0;
			float th = p2.a * 2.0 * pi + Time * 0.0698 * pow( 82.0 / max( oA, 1.0 ), 1.5 );
			float2 c0 = float2( 240.0 + oA * cos( th ), 135.0 - oB * sin( th ) );
			float2 c = lerp( c0, float2( 240.0, 135.0 ), m );
			float r0 = max( p0.b * 30.0, 1.0 );
			float r = r0 * pow( max( p2.r * 150.0, 1.0 ) / r0, zs );

			float x = ( px.x - c.x ) / r;
			float y = ( c.y - px.y ) / r;
			float r2 = x * x + y * y;
			float pa = 1.0 - smoothstep( 1.0 - 3.0 / r, 1.0, r2 );
			float z = sqrt( max( 0.0, 1.0 - r2 ) );
			float spin = Time * 0.08 * ( p1.g * 255.0 + 1.0 );
			#ifdef PDX_OPENGL
				float lon = atan( x, z ) + spin;
			#else
				float lon = atan2( x, z ) + spin;
			#endif
			float lat = asin( clamp( y, -1.0, 1.0 ) );
			float mu = frac( lon / ( 2.0 * pi ) + 0.5 );
			float mv = clamp( 0.5 - lat / pi, 0.0, 0.9999 );
			float mb = floor( mv * 5.0 );
			float mrow = clamp( mv * 5.0 - mb, 0.5 / 135.0, 1.0 - 0.5 / 135.0 );
			float4 tx = tex2D( MapTexture, float2( ( mb * 940.0 + 2.0 + mu * 936.0 ) / 4800.0, mrow ) );
			float3 albedo = tx.rgb;
			// v23 凹凸：alpha = 高度图，向东/向北各取一点求梯度，扰动法线
			float muE = frac( mu + 1.5 / 936.0 );
			float hE = tex2D( MapTexture, float2( ( mb * 940.0 + 2.0 + muE * 936.0 ) / 4800.0, mrow ) ).a;
			float mvN = clamp( mv - 1.5 / 675.0, 0.0, 0.9999 );
			float mbN = floor( mvN * 5.0 );
			float mrowN = clamp( mvN * 5.0 - mbN, 0.5 / 135.0, 1.0 - 0.5 / 135.0 );
			float hN = tex2D( MapTexture, float2( ( mbN * 940.0 + 2.0 + mu * 936.0 ) / 4800.0, mrowN ) ).a;
			float bk = p2.b * 7.0 * saturate( r / 40.0 );
			float3 N0 = float3( x, y, z );
			float cxz = max( sqrt( x * x + z * z ), 0.001 );
			float3 Te = float3( z, 0.0, -x ) / cxz;
			float3 Tn = float3( -y * x / cxz, cxz, -y * z / cxz );
			float3 Nb = normalize( N0 - bk * ( ( hE - tx.a ) * Te + ( hN - tx.a ) * Tn ) );
			float2 sd = normalize( float2( 240.0 - c0.x, c0.y - 135.0 ) + float2( 0.0001, 0.0 ) );
			float3 L = normalize( float3( sd, 0.45 ) );
			float ndl0 = dot( N0, L );
			float ndl = dot( Nb, L );
			float lit = smoothstep( -0.08, 0.25, ndl0 ) * saturate( 0.55 + 0.45 * ndl + 0.6 * ( ndl - ndl0 ) );
			float atm = p1.b * 255.0 / 40.0;
			float rim = pow( 1.0 - z, 2.2 ) * atm * 0.75 * smoothstep( -0.25, 0.35, ndl0 );
			float3 col = albedo * ( 0.035 + 0.965 * lit ) + float3( 0.35, 0.6, 1.0 ) * rim;
			// v23 大气外辉光（地球/金星/冰巨星，p1.b > 0）：盘外指数衰减，亮面更强
			float sr = sqrt( r2 );
			float2 ld = normalize( L.xy );
			float2 pd = float2( x, y ) / max( sr, 0.001 );
			float hl = 0.25 + 0.75 * smoothstep( -0.35, 0.6, dot( pd, ld ) );
			float ha = saturate( exp( -max( sr - 1.0, 0.0 ) / 0.07 ) * step( 1.0, sr + 0.02 ) * atm * 0.85 * hl ) * saturate( r / 6.0 );
			float3 hcol = float3( 0.42, 0.68, 1.0 );

			if ( p2.g > 0.5 )
			{
				float ex = x / 2.3;
				float ey = y / ( 2.3 * 0.34 );
				float er = sqrt( ex * ex + ey * ey );
				float rt = clamp( ( er - 0.47 ) / 0.53, 0.5 / 135.0, 1.0 - 0.5 / 135.0 );
				float on = step( 0.47, er ) * step( er, 1.0 );
				float3 rc = tex2D( MapTexture, float2( 4770.0 / 4800.0, rt ) ).rgb;
				float ra = tex2D( MapTexture, float2( 4790.0 / 4800.0, rt ) ).r * on;
				float ab = ra * step( 0.0, y ) * ( 1.0 - pa );
				col = ( col * pa + rc * ab ) / max( pa + ab, 0.001 );
				pa = pa + ab;
				float af = ra * step( y, 0.0 );
				col = lerp( col, rc, af / max( pa * ( 1.0 - af ) + af, 0.001 ) );
				pa = pa * ( 1.0 - af ) + af;
			}

			float da = smoothstep( 0.0, 0.45, t ) * 0.93;
			float3 dim = float3( 0.024, 0.067, 0.082 );
			// v24d 遮挡：轨道远侧（sin th > 0）时，太阳盘面（半径约 26px）挡住行星
			float sdist = length( px - float2( 240.0, 135.0 ) );
			float occ = 1.0 - smoothstep( 0.0, 0.08, sin( th ) ) * ( 1.0 - smoothstep( 24.0, 28.0, sdist ) ) * ( 1.0 - m );
			pa = pa * occ;
			ha = ha * occ;
			ha = ha * ( 1.0 - pa );
			float aq = pa + ha;
			float3 fr = col * pa + hcol * ha;
			float oa = aq + da * ( 1.0 - aq );
			return float4( ( fr + dim * da * ( 1.0 - aq ) ) / max( oa, 0.001 ), oa );
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
	PixelShader = "PixelShaderNSPOrbit"
}
Effect Down
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderNSPOrbit"
}
Effect Disable
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderNSPOrbit"
}
Effect Over
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderNSPOrbit"
}
