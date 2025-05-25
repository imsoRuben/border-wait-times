import * as React from 'react';
import { useEffect, useState } from 'react';
import { View as SkeletonView } from 'react-native';
import * as Location from 'expo-location';
import moment from 'moment';
import { Text, View, ActivityIndicator, FlatList, StyleSheet, RefreshControl, TextInput, ActionSheetIOS, Pressable } from 'react-native';
import { useRouter } from 'expo-router';


interface LaneDetail {
  delay_minutes?: number | string;
  lanes_open?: number;
}

interface PassengerVehicleLanes {
  standard_lanes?: LaneDetail;
  ready_lanes?: LaneDetail;
  sentri_lanes?: LaneDetail;
  NEXUS_lanes?: LaneDetail;
}

interface CommercialVehicleLanes {
  standard_lanes?: LaneDetail;
  FAST_lanes?: LaneDetail;
}

interface PedestrianLanes {
  standard_lanes?: LaneDetail;
  ready_lanes?: LaneDetail;
}

interface WaitTimeItem {
  crossing_name: string;
  port_name: string;
  border: string;
  date: string;
  time: string;
  passenger_vehicle_lanes?: PassengerVehicleLanes;
  commercial_vehicle_lanes?: CommercialVehicleLanes;
  pedestrian_lanes?: PedestrianLanes;
  construction_notice?: string;
}

const cleanPortLabel = (crossing: string, port: string): string => {
  const cleanedCrossing = (crossing ?? '').replace(/^\(|\)$/g, '').trim();
  const safePort = port ?? '';
  if (!cleanedCrossing || cleanedCrossing.toLowerCase() === safePort.toLowerCase()) {
    return safePort;
  }
  return `${cleanedCrossing} (${safePort})`;
};

export default function ExploreScreen() {
  const [data, setData] = useState<WaitTimeItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [userLocation, setUserLocation] = useState<{ latitude: number; longitude: number } | null>(null);
  const [sortBy, setSortBy] = useState<'proximity' | 'alphabetical' | 'passenger' | 'pedestrian' | 'commercial' | 'ready' | 'sentri'>('proximity');
  const [lastFetched, setLastFetched] = useState<Date | null>(null);
  const router = useRouter();

  const fetchWaitTimes = async () => {
    try {
      setError('');
      const response = await fetch('https://border-wait-times.onrender.com/wait-times');
      const json = await response.json();
      console.log("API Response:", json);
      console.log("Ports returned:", json?.all_ports_summary?.length);
      console.log("Sample Port Data:", JSON.stringify(json.all_ports_summary?.[0], null, 2));
      setData(json.all_ports_summary);
      setLastFetched(new Date());
    } catch (err) {
      console.error("API Error:", err);
      setError('Failed to load wait times.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    const getLocationAndFetch = async () => {
      console.log("Attempting to request location permissions...");
      let { status } = await Location.requestForegroundPermissionsAsync();
      console.log("Permission status:", status);
      if (status === 'granted') {
        let location = await Location.getCurrentPositionAsync({});
        setUserLocation({
          latitude: location.coords.latitude,
          longitude: location.coords.longitude,
        });
      }
      fetchWaitTimes();
    };

    getLocationAndFetch();
  }, []);

  const onRefresh = () => {
    setRefreshing(true);
    fetchWaitTimes();
  };

  const getDelayStyle = (delay: number | undefined) => {
    if (typeof delay !== 'number') return styles.text;
    if (delay <= 10) return [styles.text, styles.short];
    if (delay >= 30) return [styles.text, styles.long];
    return styles.text;
  };

  const getDelayMessage = (delay?: number) => {
    if (delay === undefined) return null;
    return (
      <Text style={[styles.badge, delay > 20 ? styles.long : styles.short]}>
        {delay > 20 ? 'Longer than usual' : 'Shorter than usual'}
      </Text>
    );
  };

  const getDistance = (lat1: number, lon1: number, lat2: number, lon2: number) => {
    const R = 6371; // Radius of the Earth in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a =
      0.5 - Math.cos(dLat)/2 +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
      (1 - Math.cos(dLon)) / 2;
    return R * 2 * Math.asin(Math.sqrt(a));
  };

  const uniqueData = (() => {
    const labelCount: Record<string, number> = {};
    const result: WaitTimeItem[] = [];

    for (const item of data) {
      const label = `${item.crossing_name}-${item.port_name}`;
      if (!labelCount[label]) {
        labelCount[label] = 1;
      } else {
        labelCount[label]++;
      }

      // Attach a suffix to distinguish duplicates
      const suffix = labelCount[label] > 1 ? ` (${labelCount[label]})` : '';
      result.push({ ...item, port_name: item.port_name + suffix });
    }

    return result;
  })();

  const filteredData = [...uniqueData]
    .filter(item =>
      (item.crossing_name?.toLowerCase() || '').includes(searchQuery.toLowerCase()) ||
      (item.port_name?.toLowerCase() || '').includes(searchQuery.toLowerCase())
    )
    .sort((a, b) => {
      if (sortBy === 'alphabetical') {
        return cleanPortLabel(a.crossing_name, a.port_name).localeCompare(
          cleanPortLabel(b.crossing_name, b.port_name)
        );
      }

      if (sortBy === 'passenger') {
        return (
          parseInt(String(a.passenger_vehicle_lanes?.standard_lanes?.delay_minutes ?? '9999'), 10) -
          parseInt(String(b.passenger_vehicle_lanes?.standard_lanes?.delay_minutes ?? '9999'), 10)
        );
      }

      if (sortBy === 'ready') {
        return (
          parseInt(String(a.passenger_vehicle_lanes?.ready_lanes?.delay_minutes ?? '9999'), 10) -
          parseInt(String(b.passenger_vehicle_lanes?.ready_lanes?.delay_minutes ?? '9999'), 10)
        );
      }

      if (sortBy === 'sentri') {
        return (
          parseInt(String(a.passenger_vehicle_lanes?.sentri_lanes?.delay_minutes ?? '9999'), 10) -
          parseInt(String(b.passenger_vehicle_lanes?.sentri_lanes?.delay_minutes ?? '9999'), 10)
        );
      }

      if (sortBy === 'pedestrian') {
        return (
          (Number(a.pedestrian_lanes?.standard_lanes?.delay_minutes) ?? Infinity) -
          (Number(b.pedestrian_lanes?.standard_lanes?.delay_minutes) ?? Infinity)
        );
      }

      if (sortBy === 'commercial') {
        return (
          (Number(a.commercial_vehicle_lanes?.standard_lanes?.delay_minutes) ?? Infinity) -
          (Number(b.commercial_vehicle_lanes?.standard_lanes?.delay_minutes) ?? Infinity)
        );
      }

      if (!userLocation) return 0;

      const portCoords: Record<string, { lat: number; lon: number }> = {
        'Deconcini': { lat: 31.3337, lon: -110.9398 },
        'Mariposa': { lat: 31.4640, lon: -110.9616 },
        'Morley Gate': { lat: 31.3327, lon: -110.9372 },
        'Otay Mesa': { lat: 32.5515, lon: -116.9335 },
        'Paso Del Norte': { lat: 31.7586, lon: -106.4869 },
      };
      const aCoords = portCoords[a.crossing_name] ?? { lat: 0, lon: 0 };
      const bCoords = portCoords[b.crossing_name] ?? { lat: 0, lon: 0 };
      const distA = getDistance(userLocation.latitude, userLocation.longitude, Number(aCoords.lat), Number(aCoords.lon));
      const distB = getDistance(userLocation.latitude, userLocation.longitude, Number(bCoords.lat), Number(bCoords.lon));
      return distA - distB;
    });

  const lastUpdated = lastFetched
    ? moment(lastFetched).fromNow()
    : '';

  // Helper for formatting
  const formatDelay = (delay: any) =>
    delay === null || delay === undefined || delay === '' ? null : parseInt(delay, 10);

  // Mapping lane keys to display names
  const labelMap: Record<string, string> = {
    standard_lanes: 'General',
    ready_lanes: 'ReadyLane',
    sentri_lanes: 'SENTRI',
    NEXUS_lanes: 'NEXUS',
    FAST_lanes: 'FAST',
  };

  // Helper to format lane info
  const formatLaneInfo = (delay: any, lanes: any) => {
    const parsedDelay = typeof delay === 'string' ? parseInt(delay) : delay;
    const parsedLanes = typeof lanes === 'string' ? parseInt(lanes) : lanes;
    const hasDelay = typeof parsedDelay === 'number' && !isNaN(parsedDelay);
    const hasLanes = typeof parsedLanes === 'number' && !isNaN(parsedLanes) && parsedLanes >= 0;
    if (!hasDelay && !hasLanes) return 'Not available';
    if (hasDelay && hasLanes) return `${parsedDelay} min delay • ${parsedLanes} lane${parsedLanes === 1 ? '' : 's'} open`;
    if (hasDelay) return `${parsedDelay} min delay`;
    if (hasLanes) return `${parsedLanes} lane${parsedLanes === 1 ? '' : 's'} open`;
    return 'Not available';
  };

  // Helper to render a lane group dynamically
  const renderLaneGroup = (laneGroup: any) => {
    if (!laneGroup) return (
      <Text style={styles.noData}>No data</Text>
    );
    return Object.keys(laneGroup).map((laneKey) => {
      const laneDetail = laneGroup[laneKey];
      const label = labelMap[laneKey] || laneKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
      return (
        <Text style={styles.text} key={laneKey}>
          <Text style={{ fontWeight: 'bold' }}>{label}:</Text>
          <Text> {formatLaneInfo(formatDelay(laneDetail?.delay_minutes), laneDetail?.lanes_open)}</Text>
        </Text>
      );
    });
  };

  const renderItem = ({ item }: { item: WaitTimeItem }) => {
    return (
      <Pressable
        onPress={() =>
          router.push({
            pathname: '../port-detail',
            params: { data: JSON.stringify(item) },
          })
        }
      >
        <View style={styles.item}>
          <Text style={styles.cornerBadge}></Text>
          <Text style={styles.title} numberOfLines={1} ellipsizeMode="tail">
            {cleanPortLabel(item.crossing_name, item.port_name)}
          </Text>

          {/* Passenger Vehicles */}
          <Text style={styles.sectionHeader}>🚗 Passenger Vehicles</Text>
          {renderLaneGroup(item.passenger_vehicle_lanes)}

          {/* Pedestrian */}
          <Text style={styles.sectionHeader}>🚶 Pedestrian</Text>
          {renderLaneGroup(item.pedestrian_lanes)}

          {/* Commercial Vehicles */}
          <Text style={styles.sectionHeader}>🚛 Commercial Vehicles</Text>
          {renderLaneGroup(item.commercial_vehicle_lanes)}
        </View>
      </Pressable>
    );
  };

  if (loading) {
    return (
      <View style={{ padding: 16 }}>
        {[...Array(5)].map((_, index) => (
          <React.Fragment key={index}>
            <View style={{ marginBottom: 16 }}>
              <SkeletonView style={{ width: 200, height: 20, backgroundColor: '#E1E9EE', marginBottom: 6 }} />
              <SkeletonView style={{ width: 250, height: 16, backgroundColor: '#E1E9EE', marginBottom: 4 }} />
              <SkeletonView style={{ width: 250, height: 16, backgroundColor: '#E1E9EE', marginBottom: 4 }} />
              <SkeletonView style={{ width: 250, height: 16, backgroundColor: '#E1E9EE' }} />
            </View>
          </React.Fragment>
        ))}
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.container}>
        <Text style={styles.error}>{error}</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {lastUpdated ? (
        <Text style={styles.timestamp}>Last updated: {lastUpdated}</Text>
      ) : null}
      <TextInput
        style={styles.searchInput}
        placeholder="Search by port or crossing name"
        value={searchQuery}
        onChangeText={setSearchQuery}
      />
      <View style={{ marginBottom: 16, flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
        <Pressable
          style={{ flexDirection: 'row', alignItems: 'center' }}
          onPress={() =>
            ActionSheetIOS.showActionSheetWithOptions(
              {
                options: [
                  'Cancel',
                  'Proximity',
                  'Alphabetical',
                  'Passenger Wait',
                  'Pedestrian Wait',
                  'Commercial Wait',
                ],
                cancelButtonIndex: 0,
              },
              (buttonIndex) => {
                if (buttonIndex === 1) setSortBy('proximity');
                else if (buttonIndex === 2) setSortBy('alphabetical');
                else if (buttonIndex === 3) setSortBy('passenger');
                else if (buttonIndex === 4) setSortBy('pedestrian');
                else if (buttonIndex === 5) setSortBy('commercial');
              }
            )
          }
        >
          <Text style={{ fontSize: 14, color: '#555', marginRight: 4 }}>Sort by:</Text>
          <Text style={{ fontSize: 14, color: '#007aff', fontWeight: '500' }}>
            {sortBy.charAt(0).toUpperCase() + sortBy.slice(1)}
          </Text>
        </Pressable>
      </View>
      <FlatList
        data={filteredData}
        keyExtractor={(item) => `${item.port_name}-${item.crossing_name}-${item.date}`}
        renderItem={renderItem}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  sectionHeader: {
    fontWeight: 'bold',
    marginTop: 12,
    marginBottom: 4,
    fontSize: 16,
  },
  loading: {
    flex: 1,
    justifyContent: 'center',
  },
  item: {
    marginBottom: 16,
    padding: 12,
    borderRadius: 8,
    backgroundColor: '#f0f0f0',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  title: {
    fontWeight: 'bold',
    fontSize: 22,
    marginBottom: 4,
  },
  short: {
    color: 'green',
    fontWeight: 'bold',
  },
  long: {
    color: 'red',
    fontWeight: 'bold',
  },
  text: {
    fontSize: 16,
    fontFamily: 'Courier',
  },
  error: {
    color: 'red',
    fontSize: 18,
  },
  searchInput: {
    height: 40,
    borderColor: '#ccc',
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 10,
    marginBottom: 16,
  },
  timestamp: {
    fontSize: 12,
    color: '#555',
    textAlign: 'right',
    marginBottom: 4,
  },
  cornerBadge: {
    position: 'absolute',
    top: 4,
    right: 8,
    fontSize: 16,
    opacity: 0.6,
    width: 20,
    textAlign: 'right',
  },
  badge: {
    backgroundColor: '#eee',
    borderRadius: 6,
    paddingHorizontal: 6,
    paddingVertical: 2,
    marginTop: 2,
    alignSelf: 'flex-start',
    fontSize: 14,
  },
  delayNote: {
    fontSize: 14,
    fontFamily: 'System',
    marginLeft: 4,
  },
  delayNoteShort: {
    color: 'green',
    fontWeight: '600',
  },
  delayNoteLong: {
    color: 'red',
    fontWeight: '600',
  },
  noData: {
    fontStyle: 'italic',
    color: '#888',
  },
  notice: {
    fontSize: 14,
    color: '#aa6600',
    marginBottom: 4,
    fontStyle: 'italic',
  },
  picker: {
    height: 40,
    width: '100%',
    marginBottom: 8,
  },
  statusText: {
    fontSize: 14,
    color: '#555',
    marginBottom: 4,
  },
});