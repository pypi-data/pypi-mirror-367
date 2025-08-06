import 'package:flet/flet.dart';
import 'package:flet_cacheimg/src/flet_cacheimg.dart';
import 'package:flet_cacheimg/src/flet_cacheavatar.dart';
CreateControlFactory createControl = (CreateControlArgs args) {
  final type = args.control.type.trim().toLowerCase();

  switch (type) {
    case "flet_cacheimg":
      return FletCacheImgControl(
        key: args.key,
        parent: args.parent,
        children: args.children,
        control: args.control,
        parentDisabled: args.parentDisabled,
        parentAdaptive: args.parentAdaptive,
        backend: args.backend,
      );

    case "flet_cache_circle_avatar":
      return FletCacheCircleAvatarControl(
        key: args.key,
        parent: args.parent,
        children: args.children,
        control: args.control,
        parentDisabled: args.parentDisabled,
        backend: args.backend,
      );

    default:
      return null;
  }
};

void ensureInitialized() {
  print("flet_cacheimg.ensureInitialized called");
}
