
build: clean target target/cloudwatch_humio.zip

clean:
	rm -rf target/cloudwatch_humio.zip

init:
	terraform init
	cd test && $(MAKE) init

target:
	mkdir -p target

target/cloudwatch_humio.zip:
	(cd lambdas/ && zip -r ../target/cloudwatch_humio.zip * )

clean:
	rm -rf target

plan: build
	terraform plan

apply: build
	terraform apply

destroy:
	terraform destroy -force

.PHONY: plan clean apply destroy init
