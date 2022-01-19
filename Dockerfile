FROM datajoint/djlab:py3.8-debian

USER root
RUN apt-get update -y
RUN apt-get install git -y

USER anaconda
WORKDIR /main/workflow-array-ephys

# Option 1 - Install DataJoint's remote fork of the workflow and elements
RUN git clone https://github.com/datajoint/workflow-array-ephys.git .

# Option 2 - Install user's remote fork of element and workflow
#            or an unreleased version of the element
# RUN pip install git+https://github.com/<user>/element-array-ephys.git
# RUN git clone https://github.com/<user>/workflow-array-ephys.git /main/workflow-array-ephys

# Option 3 - Install user's local fork of element and workflow
# RUN mkdir /main/element-array-ephys
# COPY --chown=anaconda:anaconda ./element-array-ephys /main/element-array-ephys
# RUN pip install /main/element-array-ephys
# COPY --chown=anaconda:anaconda ./workflow-array-ephys /main/workflow-array-ephys
# RUN rm /main/workflow-array-ephys/dj_local_conf.json

# Install the workflow
RUN pip install /main/workflow-array-ephys
RUN pip install -r /main/workflow-array-ephys/requirements_test.txt
