AYON_ADDON_VERSION=$(shell python -c "import os;import sys;content={};f=open('$(CURDIR)/../../package.py');exec(f.read(),content);f.close();print(content['version'])")
AYON_ADDON_NAME=hierarchytemplate
SERVICE_NAME=processor
BASE_NAME := ash-$(AYON_ADDON_NAME)-$(SERVICE_NAME)
IMAGE := doerp/$(BASE_NAME):$(AYON_ADDON_VERSION)

build:
	docker build -t $(IMAGE) -f Dockerfile . --no-cache

push:
	docker push $(IMAGE)
