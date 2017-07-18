package compare_measures.measures;

import compare_measures.Draw;

public class MSpecAsym extends aMeasure {

	@Override
	public String getName() {
		return "Specific Asymmetry";
	}

	@Override
	public String getAbbr() {
		return "SA";
	}

	@Override
	public double getScore(Draw draw) {
		double inverse_pct = 1-draw.popular_pct;
		double seats = 0;
		double inverse_seats = 0;
		
		for( int i = 0; i < draw.centered_district_pcts.length; i++) {
			double rep = draw.centered_district_pcts[i];
			double dem = 1-draw.centered_district_pcts[i];
			if( rep*draw.popular_pct > dem*inverse_pct) {
				seats++;
			}
			if( rep*inverse_pct < dem*draw.popular_pct) {
				inverse_seats++;
			}
		}
		
		return ((seats-inverse_seats))/(double)draw.centered_district_pcts.length;
	}

	@Override
	public double getLowerBound() {
		return -1;
	}

	@Override
	public double getUpperBound() {
		return 1;
	}
}
