#!/usr/bin/env python3
"""Abaisse la cible iOS de Moonfin (Moonfin-Core) et de son moteur AetherEngine.
Usage : python3 patch-ios-min.py <racine Moonfin-Core> <version min, ex. 16.0>
A lancer apres avoir clone AetherEngine dans ios/Packages/AetherEngine."""
import pathlib, re, sys

root = pathlib.Path(sys.argv[1]); mini = sys.argv[2]
major = mini.split('.')[0]

# 1) Runner : IPHONEOS_DEPLOYMENT_TARGET + paquet AetherEngine local
pbx = root / 'ios/Runner.xcodeproj/project.pbxproj'
t = pbx.read_text()
t = re.sub(r'IPHONEOS_DEPLOYMENT_TARGET = 18\.0;', f'IPHONEOS_DEPLOYMENT_TARGET = {mini};', t)
t = re.sub(r'(C40E203472430991A26271B6 /\* XCRemoteSwiftPackageReference "AetherEngine" \*/ = \{)'
           r'.*?\n\t\t\};\n',
           'C40E203472430991A26271B6 /* XCLocalSwiftPackageReference "AetherEngine" */ = {\n'
           '\t\t\tisa = XCLocalSwiftPackageReference;\n'
           '\t\t\trelativePath = Packages/AetherEngine;\n\t\t};\n', t, flags=re.S)
t = t.replace('XCRemoteSwiftPackageReference "AetherEngine"', 'XCLocalSwiftPackageReference "AetherEngine"')
# deplacer le bloc dans la section Local (Xcode tolere, mais on reste propre)
blk = re.search(r'\t\tC40E203472430991A26271B6 /\* XCLocalSwiftPackageReference "AetherEngine" \*/ = \{.*?\n\t\t\};\n', t, re.S).group(0)
t = t.replace(blk, '')
t = t.replace('/* End XCLocalSwiftPackageReference section */', blk + '/* End XCLocalSwiftPackageReference section */')
pbx.write_text(t)

# 2) Podfile
pod = root / 'ios/Podfile'
pod.write_text(pod.read_text().replace("platform :ios, '18.0'", f"platform :ios, '{mini}'"))

# 3) AetherEngine : plancher iOS
pk = root / 'ios/Packages/AetherEngine/Package.swift'
pk.write_text(pk.read_text().replace('.iOS(.v18)', f'.iOS("{mini}")'))

# 4) Package.resolved : retirer l'epingle distante d'AetherEngine
for res in root.glob('ios/**/Package.resolved'):
    s = res.read_text()
    s2 = re.sub(r'\s*\{\s*"identity" : "aetherengine".*?\n    \},?', '', s, flags=re.S)
    s2 = re.sub(r',(\s*\])', r'\1', s2)
    res.write_text(s2)
print('OK : cible iOS', mini)
