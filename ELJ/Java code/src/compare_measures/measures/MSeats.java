package compare_measures.measures;

import java.util.Vector;

import compare_measures.Draw;

public class MSeats extends aMeasure {

	@Override
	public String getName() {
		return "Seat pct";
	}

	@Override
	public String getAbbr() {
		return "Seats";
	}

	@Override
	public double getScore(Draw draw) {
		return getSeatFraction(draw,draw.popular_pct);
	}

	@Override
	public double getLowerBound() {
		return 0;
	}

	@Override
	public double getUpperBound() {
		return 1;
	}
}
