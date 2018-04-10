FROM jupyter/scipy-notebook

USER root

#Sets up the repository
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y sysvinit-utils
RUN apt-get install -y apt-transport-https
RUN apt-get install -y ca-certificates
RUN apt-get install -y software-properties-common
RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

#Stable repository
RUN add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

#Installing docker CE
RUN apt-get update
RUN apt-get install -y docker-ce

RUN echo dothisagain
#XBrain section with intern
RUN git clone https://github.com/aplbrain/intern.git && cd intern && git checkout RemoteExtension && git pull && python3 setup.py install --user

#Create a local dvid repository in docker container.
RUN cd intern/xbrainDock/ && python3 dvidInit.py && python3 xBrainUpload.py

#Xbrain workflow dependencies.
RUN conda install --yes -c ilastik-forge ilastik-dependencies-no-solvers
RUN conda install --yes --force libgfortran

RUN pip install mahotas
RUN conda install --yes --force scipy
RUN pip install ndparse
