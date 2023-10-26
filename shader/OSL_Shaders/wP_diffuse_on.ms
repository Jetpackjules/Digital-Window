macroScript Diffuse_on
	category:"wParallax"
	toolTip:"wP_ON"
(
	for m in getClassInstances CoronaLegacyMtl do try(showTextureMap m false; showTextureMap m m.texmapDiffuse true) catch()

	for m in getClassInstances CoronaPhysicalMtl do try(showTextureMap m false; showTextureMap m m.baseTexmap true) catch()

	for m in getClassInstances VRayMtl do try(showTextureMap m false; showTextureMap m m.texmap_diffuse true) catch()
)
