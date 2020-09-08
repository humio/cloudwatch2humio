build: clean target copy dependencies target/cloudwatch2humio.zip

clean:
	rm -rf target/*

target:
	mkdir -p target

copy:
	cp src/* target

dependencies:
	pip3 install -r requirements.txt -t target

target/cloudwatch2humio.zip:
	(cd target/ && zip -r ../target/v.0.0.0_cloudwatch2humio.zip * )

clean:
	rm -rf target

.PHONY: clean