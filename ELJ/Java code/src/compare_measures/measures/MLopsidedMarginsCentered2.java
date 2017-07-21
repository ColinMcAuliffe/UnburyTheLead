package compare_measures.measures;

import compare_measures.Draw;

public class MLopsidedMarginsCentered2 extends aMeasure {

	@Override
	public String getName() {
		return "Lopsided Margins Centered (Arithmaticly)";
	}

	@Override
	public String getAbbr() {
		return "LMAC";
	}

	@Override
	public double getScore(Draw draw) {
		double sum_dem = 0;
		double sum_rep = 0;
		double count_dem = 0;
		double count_rep = 0;
		for( double e : draw.district_pcts) {
			double d = e - draw.popular_pct+0.5;
			if( d > 0.5) {
				sum_rep += d-0.5;
				count_rep++;
			}
			if( d < 0.5) {
				sum_dem += 0.5-d;
				count_dem++;
			}
		}
		if( count_dem == 0 || count_rep == 0) {
			return 0;
		}
		double avg_dem = sum_dem/count_dem;
		double avg_rep = sum_rep/count_rep;
		
		return avg_dem-avg_rep;
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
