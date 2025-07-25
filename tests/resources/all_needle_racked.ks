import cast_ons;

with Carrier as c:{
	cast_ons.alt_tuck_cast_on(pattern_width, tuck_lines=1, knit_lines = 0);
	cast_ons.alt_tuck_cast_on(pattern_width, is_front=False, tuck_lines=1, knit_lines = 0);
	in reverse direction:{
		knit Loops;
	}
	in reverse direction:{
		knit Loops;
	}
	Rack = 1;
	in reverse direction:{
		knit Loops;
	}
	in reverse direction:{
		knit Loops;
	}
	Rack = -1;
	in reverse direction:{
		knit Loops;
	}
	in reverse direction:{
		knit Loops;
	}
//	Rack = 0;
//	in reverse direction:{
//		knit Loops;
//	}
//	in reverse direction:{
//		knit Loops;
//	}
}
