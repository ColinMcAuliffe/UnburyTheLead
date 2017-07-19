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
		double seats = getSeatFraction(draw,draw.popular_pct);
		double inverse_seats = 1.0-getSeatFraction(draw,1.0-draw.popular_pct);
		return (seats-inverse_seats);
	}

	@Override
	public double getLowerBound() {
		return -0.5;
	}

	@Override
	public double getUpperBound() {
		return 0.5;
	}
}
