grep -qxF 'export PATH=~/bin:${PATH}' ~/.bash_profile || echo 'export PATH=~/bin:${PATH}' >> ~/.bash_profile
