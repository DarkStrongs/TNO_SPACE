# NSP v21 隐形命中区：贴图 alpha = 255（引擎点击检测要实心像素），shader 输出 alpha 0（画面上看不见）
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
	MainCode PixelShaderNSPHit
	[[
		float4 main( VS_OUTPUT v ) : PDX_COLOR
		{
			float4 c = tex2D( MapTexture, v.vTexCoord );
			return float4( c.rgb, 0.0 );
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
	PixelShader = "PixelShaderNSPHit"
}

Effect Down
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderNSPHit"
}

Effect Disable
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderNSPHit"
}

Effect Over
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderNSPHit"
}
