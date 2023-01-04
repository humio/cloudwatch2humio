build: clean target copy dependencies target/cloudwatch2logscale.zip

clean:
	rm -rf target/*

target:
	mkdir -p target

copy:
	cp src/* target

dependencies:
	pip3 install -r requirements.txt -t target

target/cloudwatch2logscale.zip:
	(cd target/ && zip -r ../target/v2.0.0_cloudwatch2logscale.zip * )

clean:
	rm -rf target

.PHONY: clean
