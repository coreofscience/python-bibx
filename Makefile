shipit:
	TAG="v`hatch version`" ;\
	git tag $$TAG && git push origin $$TAG

unship:
	TAG="v`hatch version`" ;\
	git tag -d $$TAG && git push --delete origin $$TAG
