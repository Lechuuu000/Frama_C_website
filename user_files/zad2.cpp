// getting coordinates of point with index n
void next(int n, int* x, int* y{
	*x = n%K;
	*y = n/K;
}
process Pomocniczy(int id) {
	int x, y;
	int index = id-1;
	float value;
	const int LENGTH = ceil((float)K*K/N);	// sufit		
	int newValue[LENGTH];
	tsRead("START");
	if(id == 1) {
		tsPut("No of P done with itr %d", 0);
		tsPut("Current iteration: %d", 0);
	} 
	int currentIteration = 0;
	
	while(true) {
		if(tryRead("STOP"))
			break;
		
		// calculate values for all points
		while(index < K*K) {
			next(index, &x, &y);
			tsRead("%d %d ?f", x, y, &value);
			float sum=0, temp;
			int count = 0;
			if(x != 0) {
				tsRead("%d %d ?f", x-1, y, &temp);
				count++;
				sum+=temp;
			}
			if(x != K-1) {
				tsRead("%d %d ?f", x+1, y, &temp);
				count++;
				sum+=temp;
			}
			if(y != 0) {
				tsRead("%d %d ?f", x, y-1, &temp);
				count++;
				sum+=temp;
			}
			if(y != K-1) {
				tsRead("%d %d ?f", x, y+1, &temp);
				count++;
				sum+=temp;
			}
			float newVal = A*value + (1-A)*sum/count;
			newValue[index/N] = newVal;
			if(abs(value - newVal) > epsilon) {
				if(!tryRead("Next itr needed %d", 1)) {
					int n;
					tsFetch("Next itr needed ?d", &n);
					tsPut("Next itr needed %d", 1);
				}
			}
			index+=N;
		}
		// end iteration
		int finished;
		tsFetch("No of P done with itr ?d", &finished);
		bool last = false;
		if(finished == N-1) {
			// All processes have finished their iterations, time to update values
			last = true;
			tsPut("Update values");
			tsPut("No of P done with itr %d", 0); // needed for next iteration
		} else {
			finished++;
			tsPut("No of P done with itr %d", finished);
			tsRead("Update values");
		}
		// updating values
		index = id-1;
		int i=0;
		while (index < K*K) {
			next(index, &x, &y);
			tsFetch("%d %d ?f", x, y, &value);
			tsPut("%d %d %f", x, y, newValue[i++]);
			index += N;
		}
		index = id-1;	// for next iteration
		
		if(last) {
			tsFetch("Update values");
			tsPut("Finished updating %d", 1);
			// wait for all processes to finish updating
			tsFetch("Finished updating %d", N);
			// checking if next iteration is necessary
			int nextItrNecessary;
			tsFetch("Next itr needed ?d", &nextItrNecessary);
			tsPut("Next itr needed %d", 0);	// for next iteration
			if(!nextItrNecessary) {
				tsPut("STOP");
				break;
			}
			tsFetch("Current Iteration %d", currentIteration);
			currentIteration++;
			tsPut("Current Iteration %d", currentIteration);

		} else {
			int numOfFinished;
			tsFetch("Finished updating ?d", &numOfFinished);
			tsPut("Finished updating %d", numOfFinished+1);
			// wait for the start of the next iteration
			currentIteration++;
			tsRead("Current Iteration %d", currentIteration);
		}

	}

}