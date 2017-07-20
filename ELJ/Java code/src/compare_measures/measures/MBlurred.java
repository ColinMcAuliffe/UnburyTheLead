package compare_measures.measures;

import compare_measures.Draw;

public class MBlurred extends aMeasure {

	@Override
	public String getName() {
		return "Blurred Asymmetry";
	}

	@Override
	public String getAbbr() {
		return "BA";
	}

	@Override
	public double getScore(Draw draw) {
		double area = 0;
		double inc = 0.001;
		double mean = draw.popular_pct;
		double sd = 0.05;
		double div = 0;
		for( double pct = 0; pct <= 1.0; pct += inc) {
			double seats = getSeatFraction(draw,pct);
			double inverse_seats = 1.0-getSeatFraction(draw,1.0-pct);
			double pdf = pdf(mean,sd,pct);
			area += (seats-inverse_seats)*pdf;
			div += pdf;
		}

		return area/div;
	}
	
	public double pdf(double m, double s, double x) {
		return Math.exp(-(x-m)*(x-m)/(2.0*s*s)) / Math.sqrt(2.0*Math.PI*s*s);
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
