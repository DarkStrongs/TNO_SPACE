# =============================================================================
# NSP 实时 3D 天体球（月球 / 行星）— GUI 像素着色器
# -----------------------------------------------------------------------------
# 写法照抄 Scars Radar Graph / Flaxbeard（TNO-LDOE 系 Cold Southern Springs）的
# GUI shader 骨架：Includes buttonstate.fxh + sprite_animation.fxh，取其 Time。
#
# 贴图约定（由 gen3d.py 生成）：
#   - texturefile = 方形贴图，内容是【经纬度展开图被压成正方形】，shader 自己算 UV，
#     所以贴图长宽比无所谓；元素显示尺寸用 iconType scale 控制。
#   - 左上角 1/16 方块是参数：R = 光照方位角/360（屏幕坐标，y 朝上）
#                          G = 自转档位（角速度 = 0.02 × (G+1) rad/s）
#                          B = 大气辉光强度/255
#   ⚠ 参数放贴图里而不是 frame：不依赖 scripted_gui properties，读档即生效。
# 球外像素 alpha = 0，边缘 1.5% 抗锯齿。
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
	MainCode PixelShaderNSPSphere
	[[
		float4 main( VS_OUTPUT v ) : PDX_COLOR
		{
			float pi = 3.141592654;
			float4 prm = tex2D( MapTexture, float2( 1.0 / 32.0, 1.0 / 32.0 ) );

			float x = 2.0 * v.vTexCoord.x - 1.0;
			float y = 1.0 - 2.0 * v.vTexCoord.y;
			float r2 = x * x + y * y;
			float edge = 1.0 - smoothstep( 0.97, 1.0, r2 );
			float z = sqrt( max( 0.0, 1.0 - r2 ) );

			float spin = Time * 0.08 * ( prm.g * 255.0 + 1.0 );
			#ifdef PDX_OPENGL
				float lon = atan( x, z ) + spin;
			#else
				float lon = atan2( x, z ) + spin;
			#endif
			float lat = asin( clamp( y, -1.0, 1.0 ) );

			float u = lon / ( 2.0 * pi ) + 0.5;
			float vv = clamp( 0.5 - lat / pi, 0.07, 0.999 );
			float4 albedo = tex2D( MapTexture, float2( u, vv ) );

			float la = prm.r * 2.0 * pi;
			float3 L = normalize( float3( cos( la ), sin( la ), 0.45 ) );
			float3 N = float3( x, y, z );
			float ndl = dot( N, L );
			float lit = smoothstep( -0.08, 0.25, ndl ) * ( 0.55 + 0.45 * max( ndl, 0.0 ) );
			float shade = 0.035 + 0.965 * lit;

			float rim = pow( 1.0 - z, 3.0 ) * prm.b * 2.0 * smoothstep( -0.2, 0.4, ndl );
			float3 col = albedo.rgb * shade + float3( 0.35, 0.6, 1.0 ) * rim;

			return float4( col, edge );
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
	PixelShader = "PixelShaderNSPSphere"
}
Effect Down
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderNSPSphere"
}
Effect Disable
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderNSPSphere"
}
Effect Over
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderNSPSphere"
}
