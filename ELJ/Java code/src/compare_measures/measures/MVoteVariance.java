package compare_measures.measures;

import java.util.Vector;

import compare_measures.Draw;

public class MVoteVariance extends aMeasure {

	@Override
	public String getName() {
		return "Standard deviation of vote among districts";
	}

	@Override
	public String getAbbr() {
		return "Spread";
	}

	@Override
	public double getScore(Draw draw) {
		if( draw.centered_district_pcts.length < 2) {
			return 0;
		}
		double mean = 0;
		for( int i = 0; i < draw.centered_district_pcts.length; i++) {
			mean += draw.centered_district_pcts[i];
		}
		mean /= (double)draw.centered_district_pcts.length;
		double var = 0;
		for( int i = 0; i < draw.centered_district_pcts.length; i++) {
			double diff = draw.centered_district_pcts[i]-mean;
			var += diff*diff;
		}
		return Math.sqrt(var/((double)draw.centered_district_pcts.length-1.0));
	}

	@Override
	public double getLowerBound() {
		return 0;
	}

	@Override
	public double getUpperBound() {
		return 0.5;
	}
}
