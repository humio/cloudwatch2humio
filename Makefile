build: clean target copy dependencies target/cloudwatch_humio.zip

clean:
	rm -rf target/cloudwatch_humio.zip

target:
	mkdir -p target

copy:
	cp src/* target

dependencies:
	pip3 install -r requirements.txt -t target

target/cloudwatch_humio.zip:
	(cd target/ && zip -r ../target/cloudwatch_humio.zip * )

clean:
	rm -rf target

.PHONY: clean