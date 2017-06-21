test: env
	. env/bin/activate && \
		./tests/rss-ladder && \
		./tests/rx_buffers_test.py && \
		./tests/softnet_stat_test.py && \
		./tests/server-info-show && \
		./tests/softirq_top_test.py && \
		./tests/assessor_test.py & \
		./tests/link_rate_units.sh

test3: env3
	. env3/bin/activate && \
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

env3:
	rm -rf env3
	virtualenv --python=python3 env3 && \
		. env3/bin/activate && \
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
	. env/bin/activate && \
	flake8 netutils_linux_monitoring netutils_linux_tuning netutils_linux_hardware

coverage:
	nosetests --with-coverage --cover-package=twitter

build: clean
	python setup.py sdist
	python setup.py bdist_wheel

upload: test clean
	python setup.py sdist upload
	# python setup.py bdist_wheel upload

mac_run: env
	. env/bin/activate && \
	network-top --random \
		--softirqs-file=./tests/softirqs/i7/softirqs1 \
		--softnet-stat-file=./tests/softnet_stat/softnet_stat1 \
		--interrupts-file=./tests/interrupts/singlequeue_8cpu/interrupts_short \
		--devices=eth1,eth2,eth3

mac_run_link_rate: env
	. env/bin/activate && \
	link-rate --random \
		--devices=eth1,eth2,eth3

mac_run_irqtop: env
	. env/bin/activate && \
		irqtop --random \
		--interrupts-file=./tests/interrupts/singlequeue_8cpu/interrupts_short

mac_run_softirq_top: env
	. env/bin/activate && \
	softirq-top --random \
		--softirqs-file=./tests/softirqs/i7/softirqs1

mac_run_softnet_stat_top:
	. env/bin/activate && \
	softnet-stat-top --random \
		--softnet-stat-file=./tests/softnet_stat/softnet_stat1
