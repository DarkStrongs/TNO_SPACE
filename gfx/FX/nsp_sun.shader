# =============================================================================
# NSP 实时太阳（自发光 + 双层对流 + 日冕）— GUI 像素着色器
# -----------------------------------------------------------------------------
# 写法照抄 Scars Radar Graph / Flaxbeard（TNO-LDOE 系 Cold Southern Springs）的
# GUI shader 骨架：Includes buttonstate.fxh + sprite_animation.fxh，取其 Time。
#
# 贴图 = 太阳表面经纬度图压成方形；元素四边留日冕，盘面半径 0.62。
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
			AddressU = "Wrap"
			AddressV = "Clamp"
		}
		MaskingTexture =
		{
			Index = 5
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
	MainCode PixelShaderNSPSun
	[[
		float4 main( VS_OUTPUT v ) : PDX_COLOR
		{
			float pi = 3.141592654;
			float x = 2.0 * v.vTexCoord.x - 1.0;
			float y = 1.0 - 2.0 * v.vTexCoord.y;
			float r = sqrt( x * x + y * y );
			float R = 0.62;                       // 盘面半径（其余是日冕）
			float d = r / R;
			float z = sqrt( max( 0.0, 1.0 - d * d ) );
			#ifdef PDX_OPENGL
				float lon = atan( x / R, z );
			#else
				float lon = atan2( x / R, z );
			#endif
			float lat = asin( clamp( y / R, -1.0, 1.0 ) );
			float u = lon / ( 2.0 * pi ) + 0.5;
			float vv = clamp( 0.5 - lat / pi, 0.01, 0.99 );
			float3 a = tex2D( MapTexture, float2( u + Time * 0.010, vv ) ).rgb;
			float3 b = tex2D( MapTexture, float2( u * 1.7 - Time * 0.017, vv * 1.3 + 0.2 ) ).rgb;
			float3 surf = lerp( a, b, 0.35 ) * 1.25;
			float limb = 0.45 + 0.55 * pow( z, 0.45 );
			float3 disk = surf * limb * float3( 1.05, 0.92, 0.70 );
			float inDisk = 1.0 - smoothstep( 0.985, 1.0, d );
			float pulse = 0.92 + 0.08 * sin( Time * 1.3 );
			float glow = pow( clamp( 1.0 - ( r - R ) / ( 1.0 - R ), 0.0, 1.0 ), 2.2 ) * pulse;
			float3 col = lerp( float3( 1.0, 0.62, 0.22 ), disk, inDisk );
			float alpha = max( inDisk, glow * 0.85 * ( 1.0 - inDisk ) );
			return float4( col, alpha );
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
	PixelShader = "PixelShaderNSPSun"
}
Effect Down
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderNSPSun"
}
Effect Disable
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderNSPSun"
}
Effect Over
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderNSPSun"
}
