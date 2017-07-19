package compare_measures.measures;

import compare_measures.Draw;

public class MNagle extends aMeasure {

	@Override
	public String getName() {
		return "Nagle area";
	}

	@Override
	public String getAbbr() {
		return "TotAsym";
	}

	@Override
	public double getScore(Draw draw) {
		double area = 0;
		double inc = 0.001;
		for( double pct = 0; pct < 1.0; pct += inc) {
			double seats = getSeatFraction(draw,pct);
			double inverse_seats = 1.0-getSeatFraction(draw,1.0-pct);
			area += Math.abs(seats-inverse_seats)*inc;
		}

		return area;
	}

	@Override
	public double getLowerBound() {
		return 0;
	}

	@Override
	public double getUpperBound() {
		return 0.25;
	}
}
