package compare_measures.measures;

import compare_measures.Draw;

public class MMeanMinusMedian extends aMeasure {

	@Override
	public String getName() {
		return "Mean minus median";
	}

	@Override
	public String getAbbr() {
		return "MMM";
	}

	@Override
	public double getScore(Draw draw) {
		double middle = ((double)draw.district_pcts.length-1.0)/2.0;
		double median = 0;

		median = draw.district_pcts[(int)middle];
		if( draw.district_pcts.length % 2 == 0) {
			median += draw.district_pcts[1+(int)middle];
			median /= 2;
		} else {
			
		}
		
		//flipping sign to match others
		return -(draw.popular_pct-median);
	}

	@Override
	public double getLowerBound() {
		return -0.25;
	}

	@Override
	public double getUpperBound() {
		return 0.25;
	}
}
