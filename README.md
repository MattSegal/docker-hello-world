dc logs -f --tail 200 web worker


docker tag reddit:latest 535254746276.dkr.ecr.ap-southeast-2.amazonaws.com/reddit:latest


535254746276.dkr.ecr.ap-southeast-2.amazonaws.com/reddit

	eval $(aws ecr get-login --no-include-email --region ap-southeast-2 --profile personal | sed 's|https://||')
	docker tag web:latest 535254746276.dkr.ecr.ap-southeast-2.amazonaws.com/reddit:latest
	docker push 535254746276.dkr.ecr.ap-southeast-2.amazonaws.com/reddit:latest



