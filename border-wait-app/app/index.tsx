import { View, Text, Button } from 'react-native';
import { router } from 'expo-router';

export default function HomeScreen() {
  return (
    <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
      <Text>Welcome to Border Wait Times</Text>
      <Button title="Go to Explore" onPress={() => router.push('/tabs/explore')} />
    </View>
  );
}