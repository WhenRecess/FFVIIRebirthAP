import json
from collections import defaultdict

with open('temp/BattleCharaSpec.json', 'r') as f:
    data = json.load(f)

export = data['Exports'][0]

# Collect some IDs for each prefix
prefixes = defaultdict(list)

for row in export['Data']:
    if 'Value' not in row:
        continue
    
    chara_spec_id = None
    for prop in row.get('Value', []):
        if prop.get('Name') == 'CharaSpecID':
            chara_spec_id = prop.get('Value')
            break
    
    if not chara_spec_id or not isinstance(chara_spec_id, str):
        continue
    
    prefix = chara_spec_id.split('_')[0]
    if len(prefixes[prefix]) < 5:
        prefixes[prefix].append(chara_spec_id)

# Show samples
print("Character ID Prefixes found in BattleCharaSpec:\n")
for prefix in ['EB', 'SU', 'FA', 'VE', 'VR', 'PC', 'NP', 'MM']:
    if prefix in prefixes:
        print(f"{prefix}:")
        for cid in prefixes[prefix]:
            print(f"  - {cid}")
        print()

# Count what looks like bosses (any SU, VR, or FA prefix)
boss_like = 0
for row in export['Data']:
    if 'Value' not in row:
        continue
    
    chara_spec_id = None
    for prop in row.get('Value', []):
        if prop.get('Name') == 'CharaSpecID':
            chara_spec_id = prop.get('Value')
            break
    
    if chara_spec_id and isinstance(chara_spec_id, str):
        prefix = chara_spec_id.split('_')[0]
        if prefix in ['EB', 'SU', 'FA', 'VR']:
            boss_like += 1

print(f"\nCharacters that might be bosses (EB/SU/FA/VR prefix): {boss_like}")
