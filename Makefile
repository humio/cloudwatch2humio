
build: clean target target/cloudwatch_humio.zip

clean:
	rm -rf target/cloudwatch_humio.zip

target:
	mkdir -p target

target/cloudwatch_humio.zip:
	(cd lambdas/ && zip -r ../target/cloudwatch_humio.zip * )

clean:
	rm -rf target

.PHONY: clean
