import proton

try:
    proton.main(branch='staging')
except ValueError:
    print('No pre-release branch found.')

