
''' Configuration file '''

# Repo to upload the updated dependencies
PANDORA_REPO = 'https://raw.github.com/pandora-auth-ros-pkg/ci-scripts/master/pandoradep/repos.yml'

# ROSinstall templates
INSTALL_TEMPLATE_SSH = "- git: {local-name: $name, uri: 'git@github.com:pandora-auth-ros-pkg/$name.git', version: $version}"
INSTALL_TEMPLATE_HTTPS = "- git: {local-name: $name, uri: 'https://github.com/pandora-auth-ros-pkg/$name.git', version: $version}"

# Git templates
GIT_TEMPLATE_SSH = 'git@github.com:pandora-auth-ros-pkg/$name.git'
GIT_TEMPLATE_HTTPS = 'https://github.com/pandora-auth-ros-pkg/$name.git'

# Colorscheme
COLORS = {'error': 'red',
          'success': 'green',
          'info': 'magenta',
          'debug': 'blue',
          'data': 'white',
          'warning': 'yellow'
          }

# PANDORA master branch
MASTER_BRANCH = 'hydro-devel'
