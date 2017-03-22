from rest_framework import serializers


class CoaccusedSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='officer.id')
    full_name = serializers.CharField(source='officer.full_name')
    gender = serializers.CharField(source='officer.gender_display')
    race = serializers.CharField(source='officer.race')
    final_finding = serializers.CharField(source='final_finding_display')
    recc_outcome = serializers.CharField(source='recc_outcome_display')
    final_outcome = serializers.CharField(source='final_outcome_display')
    start_date = serializers.DateField()
    end_date = serializers.DateField()


class ComplainantSerializer(serializers.Serializer):
    gender = serializers.CharField(source='gender_display')
    race = serializers.CharField()
    age = serializers.IntegerField()


class InvolvementOfficerSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    abbr_name = serializers.CharField()
    extra_info = serializers.SerializerMethodField()

    def get_extra_info(self, obj):
        return ('%s, %s' % (obj.gender_display, obj.race)).lower()


class CRSerializer(serializers.Serializer):
    crid = serializers.CharField()
    coaccused = CoaccusedSerializer(source='officer_allegations', many=True)
    complainants = ComplainantSerializer(many=True)
    point = serializers.SerializerMethodField()
    incident_date = serializers.DateTimeField(format='%Y-%m-%d')
    address = serializers.CharField()
    location = serializers.CharField()
    beat = serializers.SerializerMethodField()
    involvements = serializers.SerializerMethodField()

    def get_beat(self, obj):
        return obj.beat.id if obj.beat is not None else 'Unknown'

    def get_point(self, obj):
        if obj.point is not None:
            return {'long': obj.point.x, 'lat': obj.point.y}
        else:
            return None

    def get_involvements(self, obj):
        results = dict()
        for involvement in obj.involvement_set.filter(officer__isnull=False):
            results.setdefault(involvement.involved_type, list()).append(
                InvolvementOfficerSerializer(involvement.officer).data)
        results = [
            {'involved_type': involved_type, 'officers': officers}
            for involved_type, officers in results.iteritems()]
        return results
