test: env
	. env/bin/activate && \
		./tests/rss-ladder && \
		./tests/rx_buffers_test.py && \
		./tests/softnet_stat_test.py && \
		./tests/server-info-show && \
		./tests/softirq_top_test.py && \
		./tests/assessor_test.py & \
		./tests/link_rate_units.sh

help:
	@echo "  env         create a development environment using virtualenv"
	@echo "  deps        install dependencies"
	@echo "  clean       remove unwanted stuff"
	@echo "  lint        check style with flake8"
	@echo "  coverage    run tests with code coverage"
	@echo "  test        run tests"

env:
	rm -rf env
	virtualenv env && \
	. env/bin/activate && \
	pip install --upgrade -r requirements.txt && \
	python setup.py install

clean:
	rm -fr env
	rm -fr build
	rm -fr dist
	find . -name '*.pyc' -exec rm -f {} \;
	find . -name '*.pyo' -exec rm -f {} \;
	find . -name '*~' -exec rm -f {} \;

lint:
	flake8 twitter > violations.flake8.txt

coverage:
	nosetests --with-coverage --cover-package=twitter

build: clean
	python setup.py sdist
	python setup.py bdist_wheel

upload: test clean
	python setup.py sdist upload
	# python setup.py bdist_wheel upload

mac_run: env
	network-top --random \
		--softirqs-file=./tests/softirqs/i7/softirqs1 \
		--softnet-stat-file=./tests/softnet_stat/softnet_stat1 \
		--interrupts-file=./tests/interrupts/singlequeue_8cpu/interrupts_short \
		--devices=eth1,eth2,eth3
