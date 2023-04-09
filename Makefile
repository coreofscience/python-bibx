shipit:
	TAG="v`hatch version`" ;\
	git tag $$TAG && git push origin $$TAG
