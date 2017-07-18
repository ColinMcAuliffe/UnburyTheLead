package compare_measures.measures;

import java.util.Vector;

import compare_measures.Draw;

public class MPopularVote extends aMeasure {

	@Override
	public String getName() {
		return "Popular vote";
	}

	@Override
	public String getAbbr() {
		return "Vote";
	}

	@Override
	public double getScore(Draw draw) {
		return draw.popular_pct;
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
