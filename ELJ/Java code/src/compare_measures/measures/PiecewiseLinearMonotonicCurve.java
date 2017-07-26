package compare_measures.measures;

import java.util.Collections;
import java.util.Vector;

import compare_measures.IntegrationFunction;

public class PiecewiseLinearMonotonicCurve {
	
	boolean isCDF = false;
	
	PiecewiseLinearMonotonicCurve smoothed = null;
	int smoothed_samples = 25; 
	public void smooth() {
		//int div = (samples.size()-1)/smoothed_samples;
		int cur = 0;
		
		smoothed = new PiecewiseLinearMonotonicCurve();
		smoothed.isCDF = isCDF;
		for( int i = 0; i < samples.size()-1; i+=smoothed_samples) {
			smoothed.samples.add(samples.get(i));
		}
		smoothed.samples.add(samples.get(samples.size()-1));
	}
	
	//x = rank, y = value
	Vector<double[]> samples = new Vector<double[]>();
	
	//0 = interpolate y at x, 1 = interpolate x at y
	public double interpolate_at_v(double v, int which) {
		int xi = which;
		int yi = 1-which;
		
		int i0 = binarySearch(v,xi);
		int i1 = i0+1;
		double x0 = samples.get(i0)[xi];
		double x1 = samples.get(i1)[xi];
		double y0 = samples.get(i0)[yi];
		double y1 = samples.get(i1)[yi];
		
		double y = (x1-x0) == 0 ? y0 : y0 + (v-x0)*(y1-y0)/(x1-x0);
		
		return y;
	}
	public int binarySearch(double target_x, int which) {
		int xi = which;
		int lo_i = 0;
		int hi_i = (samples.size()-1);
		double lo_x = samples.get(lo_i)[xi];
		double hi_x = samples.get(hi_i)[xi];
		
		while( hi_i-lo_i > 1) {
			int test0 = (int)((double)(lo_i) + (target_x-lo_x)*(double)(hi_i-lo_i)/(hi_x-lo_x));
			int test1 = test0+1;
			if( test0 >= hi_i) {
				lo_i++;
				continue;
			}
			if( test1 <= lo_i) {
				hi_i--;
				continue;
			}
			
			double test_x0 = samples.get(test0)[xi];
			double test_x1 = samples.get(test1)[xi];
			if( test_x0 < target_x && test_x1 > target_x) {
				return test0;
			}
			if( test_x0 > target_x) {
				hi_i = test0;
				hi_x = test_x0;
				continue;
			}
			if( test_x1 < target_x) {
				lo_i = test1;
				lo_x = test_x1;
				continue;
			}
			if( test_x1 > target_x) {
				hi_i = test1;
				hi_x = test_x1;
				continue;
			}
			if( test_x0 < target_x) {
				lo_i = test0;
				lo_x = test_x0;
				continue;
			}
		}
		return lo_i;
	}
	
	public void sortAndRank(Vector<Double> vals, double min, double max) {
		Collections.sort(vals);
		
		samples = new Vector<double[]>();
		samples.add(new double[]{0,min});
		double inc = (max-min)/(double)(vals.size()+1);
		double cur = min+inc/2.0;
		for( int i = 0; i < vals.size(); i++) {
			samples.add(new double[]{cur,vals.get(i)});
			cur += inc;
		}
		
		samples.add(new double[]{1,max});
		
	}

	public double integrate( IntegrationFunction f) {
		double sum = 0;
		
		double lastx = samples.get(0)[0]; 
		double lasty = samples.get(0)[1]; 
		for( int i = 1; i < samples.size(); i++) {
			double x = samples.get(i)[0]; 
			double y = samples.get(i)[1];
			
			double deltay = y-lasty;
			double deltax = x-lastx;

			double midy = (y+lasty)/2.0;
			
			sum += f.f(isCDF ? deltay : midy,deltax);

			
			lastx = x;
			lasty = y;
			
		}
		return sum;
	}
	

}
