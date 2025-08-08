from yams.buildobjs import RelationDefinition


class missing_comments(RelationDefinition):
    subject = "Comment"
    name = "comments"
    object = "BlogEntry"
