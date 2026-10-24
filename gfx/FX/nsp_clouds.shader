# =============================================================================
# NSP 地球视图动态大气层（双层漂移云 + 云影）— GUI 像素着色器
# -----------------------------------------------------------------------------
# 骨架同 nsp_sphere.shader（buttonstate.fxh + sprite_animation.fxh 取 Time）。
# 贴图 nsp3d_earth_clouds.dds：RGB = 真实云图灰度，A = 地图圆角遮罩。
#   ⭐ 遮罩按原 UV 取、云按滚动 UV 取，所以云会漂、圆角不动。
#   调参：CLOUD_A 云最大不透明度；SHADOW_A 云影深度；速度见 Time 系数。
# =============================================================================
# 骨架：Includes buttonstate.fxh + sprite_animation.fxh，取其 Time。
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
	MainCode PixelShaderNSPClouds
	[[
		float4 main( VS_OUTPUT v ) : PDX_COLOR
		{
			float CLOUD_A  = 0.65;
			float ZOOM     = 0.55;   // 云块放大：越小云越大（0.55 ≈ 1.8 倍）
			float SPEED    = 0.012;  // 漂移速度（约 45 秒横穿地图）
			float SHADOW_A = 0.22;
			float2 uv = v.vTexCoord;
			float mask = tex2D( MapTexture, uv ).a;

			float wob = 0.01 * sin( Time * 0.35 + uv.x * 6.0 );
			float2 uv1 = float2( uv.x * ZOOM + Time * SPEED, uv.y * ZOOM * 1.1 + 0.2 );
			float2 uv2 = float2( uv.x * ZOOM * 1.25 + 0.37 + Time * SPEED * 0.6, clamp( uv.y * ZOOM * 1.2 + 0.15 + wob, 0.0, 1.0 ) );
			float c1 = tex2D( MapTexture, uv1 ).r;
			float c2 = tex2D( MapTexture, uv2 ).r;
			float d  = smoothstep( 0.32, 0.58, c1 * 0.7 + c2 * 0.45 );

			float2 so = float2( -0.004, -0.008 ) * ZOOM;
			float s1 = tex2D( MapTexture, uv1 + so ).r;
			float s2 = tex2D( MapTexture, uv2 + so ).r;
			float sd = smoothstep( 0.32, 0.58, s1 * 0.7 + s2 * 0.45 );

			float ca = d * CLOUD_A;
			float sa = sd * SHADOW_A * ( 1.0 - ca );
			float oa = ca + sa;
			float3 cloudCol = float3( 0.86, 0.96, 0.93 );
			float3 col = cloudCol * ca / max( oa, 0.001 );
			return float4( col, oa * mask );
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
	PixelShader = "PixelShaderNSPClouds"
}
Effect Down
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderNSPClouds"
}
Effect Disable
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderNSPClouds"
}
Effect Over
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderNSPClouds"
}
