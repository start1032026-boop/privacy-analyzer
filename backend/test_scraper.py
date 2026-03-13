from google_play_scraper import app

details = app('com.spotify.music', lang='en', country='us')

print('=== APP INFO ===')
print('Name:', details.get('title'))
print('Developer:', details.get('developer'))
print('Rating:', details.get('score'))
print('Installs:', details.get('installs'))

print('\n=== PERMISSIONS ===')
perms = details.get('permissions', [])
print('Count:', len(perms))
for p in perms[:20]:
    print(' -', p)

print('\n=== DATA SAFETY ===')
ds = details.get('dataSafety', [])
print('Count:', len(ds))
for d in ds[:10]:
    print(' -', d)

print('\n=== ALL KEYS ===')
for k, v in details.items():
    if v and k not in ['description', 'descriptionHTML', 'comments', 'screenshots', 'headerImage']:
        print(f'{k}: {str(v)[:100]}')