use std::time::{SystemTime, UNIX_EPOCH};
use zenoh_ros_type::{builtin_interfaces, std_msgs};

pub fn create_header(frame_id: &str) -> std_msgs::Header {
  let now = SystemTime::now()
    .duration_since(UNIX_EPOCH)
    .expect("Unable to get current time");

  std_msgs::Header {
    stamp: builtin_interfaces::Time {
      sec: now.as_secs() as i32,
      nanosec: now.subsec_nanos(),
    },
    frame_id: frame_id.to_string(),
  }
}
