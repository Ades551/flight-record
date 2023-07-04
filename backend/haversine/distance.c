#include <math.h>

#define RADIUS 6371  // Radius of the Earth in kilometers

// https://www.geeksforgeeks.org/haversine-formula-to-find-distance-between-two-points-on-a-sphere/
// Inspired from C++ section
double haversine(double lat1, double lon1, double lat2, double lon2) {
    double dlat = (lat2 - lat1) * M_PI / 180.0;
    double dlon = (lon2 - lon1) * M_PI / 180.0;
    double a = pow(sin(dlat/2), 2) + cos(lat1 * M_PI / 180.0) * cos(lat2 * M_PI / 180.0) * pow(sin(dlon/2), 2);
    double c = 2 * atan2(sqrt(a), sqrt(1-a));
    return RADIUS * c;
}
