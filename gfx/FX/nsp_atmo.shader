# =============================================================================
# NSP 轨道示意图地球的动态大气（球面漂移云 + 晨昏阴影 + 呼吸光晕）— GUI 像素着色器
# -----------------------------------------------------------------------------
# 骨架同 nsp_sphere.shader。叠在 GFX_NSP_trajectory 的线稿地球上（地球 r=22px，
# 元素 64×64 居中，盘面半径 = 22/32 = 0.6875，外圈是大气光晕）。
# 贴图 nsp3d_traj_atmo.dds：真实云图灰度（经纬度图压成方形）。
#   调参：CLOUD_A 云最大不透明度；NIGHT_A 夜侧压暗；HALO_A 光晕强度。
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
	MainCode PixelShaderNSPAtmo
	[[
		float4 main( VS_OUTPUT v ) : PDX_COLOR
		{
			float CLOUD_A = 0.8;
			float NIGHT_A = 0.35;
			float HALO_A  = 0.55;
			float R  = 0.6875;
			float pi = 3.141592654;

			float x = 2.0 * v.vTexCoord.x - 1.0;
			float y = 1.0 - 2.0 * v.vTexCoord.y;
			float r = sqrt( x * x + y * y );
			float d = r / R;
			float inDisk = 1.0 - smoothstep( 0.96, 1.0, d );
			float z = sqrt( max( 0.0, 1.0 - d * d ) );

			#ifdef PDX_OPENGL
				float lon = atan( x / R, z ) + Time * 0.06;
			#else
				float lon = atan2( x / R, z ) + Time * 0.06;
			#endif
			float lat = asin( clamp( y / R, -1.0, 1.0 ) );
			float u  = lon / ( 2.0 * pi ) + 0.5;
			float vv = clamp( 0.5 - lat / pi, 0.01, 0.99 );
			float c1 = tex2D( MapTexture, float2( u, vv ) ).r;
			float c2 = tex2D( MapTexture, float2( u * 1.3 + 0.41 + Time * 0.015, vv ) ).r;
			float cloud = smoothstep( 0.22, 0.75, c1 * 0.75 + c2 * 0.35 );

			float3 Ldir = normalize( float3( -0.75, 0.45, 0.6 ) );
			float ndl = dot( float3( x / R, y / R, z ), Ldir );
			float lit = smoothstep( -0.15, 0.35, ndl );

			float ca = cloud * CLOUD_A * ( 0.35 + 0.65 * lit );
			float na = NIGHT_A * ( 1.0 - lit ) * ( 1.0 - ca );
			float3 cloudCol = float3( 0.82, 0.97, 0.88 );
			float diskA = ca + na;
			float3 diskCol = cloudCol * ca / max( diskA, 0.001 );

			float limb = pow( smoothstep( 0.55, 1.0, d ), 3.0 ) * 0.35 * inDisk;
			float pulse = 0.85 + 0.15 * sin( Time * 1.1 );
			float halo = pow( clamp( 1.0 - ( r - R ) / ( 1.0 - R ), 0.0, 1.0 ), 2.0 ) * HALO_A * pulse * ( 1.0 - inDisk );
			float3 haloCol = float3( 0.45, 0.95, 0.80 );

			float a = diskA * inDisk + limb + halo;
			float3 col = ( diskCol * diskA * inDisk + haloCol * ( limb + halo ) ) / max( a, 0.001 );
			return float4( col, clamp( a, 0.0, 1.0 ) );
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
	PixelShader = "PixelShaderNSPAtmo"
}
Effect Down
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderNSPAtmo"
}
Effect Disable
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderNSPAtmo"
}
Effect Over
{
	VertexShader = "VertexShader"
	PixelShader = "PixelShaderNSPAtmo"
}
