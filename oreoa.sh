#!/bin/bash


# Initialize variables
source .env

## Function to run Zircolite
run_zircolite() {
	# Zircolite - Remove old reports
	IMAGE="alpine:latest"
	COMMAND="/bin/rm -rf /opt/report/zircolite"
	docker pull $IMAGE
	docker run --rm \
	-v $output_path:/opt/report \
	--name dfirtools \
	$IMAGE \
	$COMMAND


	# Zircolite - Generate sysmon report
	docker run --rm --tty \
	-v $input_path:/opt/data:ro \
	-v $output_path/zircolite:/opt/report \
	zircolite \
	--evtx /opt/data \
	-t /opt/report/tmp \
	--debug \
	-l /opt/report/log \
	--ruleset rules/rules_windows_sysmon_pysigma.json \
	--template templates/exportForELK.tmpl \
	--templateOutput /opt/report/exportForELK_sysmon.json \
	--template templates/exportForTimesketch.tmpl \
	--templateOutput /opt/report/exportForTimesketch_sysmon.json 

	# Zircolite - Generate generic report
	docker run --rm --tty \
	-v $input_path:/opt/data:ro \
	-v $output_path/zircolite:/opt/report \
	zircolite \
	--evtx /opt/data \
	--ruleset rules/rules_windows_generic_pysigma.json \
	--template templates/exportForELK.tmpl \
	--templateOutput /opt/report/exportForELK_generic.json \
	--template templates/exportForTimesketch.tmpl \
	--templateOutput /opt/report/exportForTimesketch_generic.json 


	if $EXPORT2ELK ; then 
	# Zircolite - Import result in ELK stack
	COMMAND="logstash -f /usr/share/logstash/pipeline/zircolite.conf"
	docker run \
		--network=elastic \
		-v $output_path/zircolite:/opt/data/ \
		logstash \
		$COMMAND

	# Zircolite - Set replicas to 0
	docker run --rm \
		--network=elastic \
		logstash \
		curl -XPUT http://elasticsearch:9200/zircolite/_settings -d '{"index":{"refresh_interval":"-1", "number_of_replicas":0}}' -H "Content-Type: application/json"
	fi
}

## Function to run Hayabusa
run_hayabusa() {
	#Hayabusa - Remove old reports
	IMAGE="alpine:latest"
	COMMAND="/bin/rm -rf /opt/report/hayabusa"
	docker pull $IMAGE
	docker run --rm \
	-v $output_path:/opt/report \
	--name dfirtools \
	$IMAGE \
	$COMMAND

	# Hayabusa - Generate jsonl report to ELK stack
	#hayabusa-2.16.0-lin-x64-gnu json-timeline -d /tmp/evidence -L -o hayabusa.json --ISO-8601 -p super-verbose
	docker run --rm --tty \
	-v $input_path:/opt/data:ro \
	-v $output_path/hayabusa:/opt/report \
	hayabusa \
	json-timeline \
	--JSONL-output \
	--ISO-8601 \
	-U \
	-m low \
	--no-wizard \
	--no-color \
	--quiet \
	-d /opt/data \
	-o /opt/report/report-hayabusa.jsonl


	if $EXPORT2TIMESKETCH ; then 
	# Hayabusa - Move result file to timesketch installation folder
	IMAGE="alpine:latest"
	COMMAND="/bin/cp -f /opt/report/report-hayabusa.jsonl /opt/timesketch/"
	docker pull $IMAGE
	docker run --rm \
		-v $output_path/hayabusa:/opt/report \
		-v $timesketch_upload_path:/opt/timesketch \
		--name dfirtools \
		$IMAGE \
		$COMMAND

	# Hayabusa - Import timeline into Timesketch
	## Test if file is empty or not befor importation step
	#  /bin/bash -c  "SIZE=$(/usr/bin/stat -c%s /usr/share/timesketch/upload/report-hayabusa.csv); if [[ $SIZE -gt 0 ]]; then timesketch_importer -u "+$timesketch_user+" -p "+$timesketch_password+" --host http://timesketch-web:5000   --timeline_name hayabusa --sketch_id 1   /usr/share/timesketch/upload/report-hayabusa.csv; fi"
	COMMAND="timesketch_importer -u $timesketch_user -p $timesketch_password --host http://timesketch-web:5000   --timeline_name hayabusa --sketch_id  $timesketch_sketch_id   /usr/share/timesketch/upload/report-hayabusa.jsonl"
	echo $COMMAND

	docker exec           \
		timesketch-worker   \
		/bin/bash -c  "$COMMAND"

	fi  

	if $EXPORT2ELK ; then 
	# Hayabusa - Update fields without names
	IMAGE="alpine:latest"
	docker pull $IMAGE
	docker run --rm \
		-v $output_path/hayabusa:/opt/report \
		--name dfirtools \
		$IMAGE \
		sed -i 's/"":/"extraData":/g' /opt/report/report-hayabusa.jsonl


	# Hayabusa - Import result in ELK stack
	COMMAND="logstash -f /usr/share/logstash/pipeline/hayabusa.conf"
	docker run \
		--network=elastic \
		-v $output_path/hayabusa:/opt/data/ \
		logstash \
		$COMMAND

	# Hayabusa - Set replicas to 0
	docker run --rm \
		--network=elastic \
		logstash \
		curl -XPUT http://elasticsearch:9200/hayabusa/_settings -d '{"index":{"refresh_interval":"-1", "number_of_replicas":0}}' -H "Content-Type: application/json"
	fi
}  

## Function to run Takajo
run_takajo(){
	# Takajo - Create output dir
	IMAGE="alpine:latest"
	COMMAND="/bin/rm -rf /opt/report/takajo"
	docker pull $IMAGE
	docker run --rm \
	-v $output_path:/opt/report \
	--name dfirtools \
	$IMAGE \
	$COMMAND

	# Takajo - Analyse Hayabusa report
	docker run --rm --tty \
	-v $output_path:/opt/report \
	takajo \
	automagic \
	-t /opt/report/hayabusa/report-hayabusa.jsonl \
	-o /opt/report/takajo
}

## Function to run Chainsaw
run_chainsaw() {
	# Chainsaw - Remove old report
	IMAGE="alpine:latest"
	COMMAND="/bin/rm -f /opt/report/report-chainsaw.json*"
	docker pull $IMAGE
	docker run --rm \
	-v $output_path/chainsaw:/opt/report \
	--name dfirtools \
	$IMAGE \
	$COMMAND

	# Chainsaw - run hunting 
	docker run --rm --tty \
	-v $input_path:/opt/data:ro \
	-v $output_path/chainsaw:/opt/report \
	chainsaw \
	hunt \
	/opt/data/ \
	-r /opt/chainsaw-src/rules/ \
	-s /opt/sigma/ \
	--skip-errors \
	--mapping /opt/chainsaw-src/mappings/sigma-event-logs-all.yml \
	--json -o /opt/report/report-chainsaw.json

	# Chainsaw - generate jsonl report
	IMAGE="alpine:latest"
	COMMAND="/sbin/apk add jq; jq -c '.[]' /opt/report/report-chainsaw.json | tee /opt/report/report-chainsaw.jsonl"
	docker pull $IMAGE
	docker run --rm \
	-v $output_path/chainsaw:/opt/report \
	--name dfirtools \
	$IMAGE \
	sh -c "$COMMAND"

	# Sync filesystem
	sync
	sleep 3

	if $EXPORT2ELK ; then 
	# Chainsaw - Import result in ELK stack
	COMMAND="logstash -f /usr/share/logstash/pipeline/chainsaw.conf"
	docker run --rm \
		--network=elastic \
		-v $output_path/chainsaw:/opt/data/ \
		logstash \
		$COMMAND

	docker run --rm \
		--network=elastic \
		logstash \
		curl -XPUT http://elasticsearch:9200/chainsaw/_settings -d '{"index":{"refresh_interval":"-1", "number_of_replicas":0}}' -H "Content-Type: application/json"
	fi

}


## Function to run Plaso
run_plaso() {
	# Plaso - Remove old report
	IMAGE="alpine:latest"
	COMMAND="rm -rf /opt/report/plaso/"
	docker pull $IMAGE
	docker run --rm \
	-v $output_path:/opt/report \
	--name dfirtools \
	$IMAGE \
	$COMMAND

	# Plaso - Create temporary folder
	IMAGE="alpine:latest"
	COMMAND="/bin/mkdir -p /opt/report/plaso/tmp"
	docker pull $IMAGE
	docker run --rm \
	-v $output_path:/opt/report \
	--name dfirtools \
	$IMAGE \
	$COMMAND

	# Plaso - start timeline generation
	docker run --rm \
	-v $input_path:/opt/data:ro \
	-v $output_path/plaso:/opt/report \
	plaso log2timeline \
	-z UTC \
	--storage_file /opt/report/plaso_log2timeline.plaso \
	--partitions all \
	--volumes all \
	--logfile /opt/report/plaso_log2timeline.log.gz \
	--temporary_directory /opt/report/tmp/ \
	/opt/data

	if $EXPORT2TIMESKETCH ; then 
		# Plaso - Move result file to timesketch
		IMAGE="alpine:latest"
		COMMAND="/bin/cp -f /opt/plaso/plaso_log2timeline.plaso /opt/timesketch/ "
		docker pull $IMAGE
		docker run --rm \
			-v $output_path/plaso:/opt/plaso \
			-v $timesketch_upload_path:/opt/timesketch \
			--name dfirtools \
			$IMAGE \
			$COMMAND

		# Plaso - Import timeline into Timesketch
		COMMAND="timesketch_importer -u $timesketch_user -p $timesketch_password --host http://timesketch-web:5000   --timeline_name plaso_log2timeline --sketch_id  $timesketch_sketch_id  /usr/share/timesketch/upload/plaso_log2timeline.plaso"
		docker exec           \
			timesketch-worker   \
			/bin/bash -c  "$COMMAND"
	fi

	if $EXPORT2ELK ; then 
		# Plaso - Import timeline in ELK stack
		docker run --rm \
			--network=elastic \
			-v $output_path/plaso:/opt/report \
			plaso psort \
			--analysis tagging \
			--tagging-file /opt/plaso/src/plaso/data/tag_$os.txt \
			--output_time_zone UTC \
			-o opensearch \
			--opensearch-server elasticsearch \
			--opensearch-port 9200 \
			--opensearch-mappings /opt/plaso/src/plaso/data/opensearch.mappings \
			--index_name log2timeline \
			/opt/report/plaso_log2timeline.plaso

		# Plaso - set Index replicas to 0
		docker run --rm \
			--network=elastic \
			logstash \
			curl -XPUT http://elasticsearch:9200/log2timeline/_settings -d '{"index":{"refresh_interval":"-1", "number_of_replicas":0}}' -H "Content-Type: application/json"
	fi	
}


## Function to generate hashes
generate_hashes() {
	IMAGE="ubuntu:latest"
	COMMAND="apt update; apt install -y hashdeep; hashdeep -r -c sha256 -l /opt/report/ | tee /opt/report/hashdeep.log"
	docker pull $IMAGE
	docker run --rm \
	  -v $output_path:/opt/report \
	  --name dfirtools_ubuntu \
	  $IMAGE \
	  sh -c "$COMMAND"
}


# Step 1 - run zircolite -- Disabled by default / Issue with the high numbers of evtx files
#run_zircolite
#sleep 5

# Step 2 - run hayabusa
run_hayabusa
sleep 5

# Step 3 - run takajo
run_takajo
sleep 5

# Step 4 - run chainsaw -- Disabled by default / Stay stuck without error
#run_chainsaw
#sleep 5

# Step 5 - run plaso
run_plaso
sleep 5

# Step 6 - generate hashes
generate_hashes
sleep 5



