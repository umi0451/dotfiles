. "$XDG_CONFIG_HOME/lib/unittest.bash"
. "$XDG_CONFIG_HOME/lib/utils.bash"

should_panic() {
	assertOutputEqual 'panic "ERROR" 2>&1; echo "this should not happen"' 'ERROR'
	assertExitFailure
}

should_perform_actions_finally() {
	assertOutputEqual "( finally 'echo finally'; echo 'test' )" "test\nfinally"
}

should_accumulate_finally_statements() {
	assertOutputEqual "( finally 'echo first finally'; echo 'test'; finally 'echo second finally';  )" "test\nfirst finally\nsecond finally"
}

should_perform_finally_in_separate_subshells_independently() {
	assertOutputEqual "( finally 'echo first'; echo 'test' )" "test\nfirst"
	assertOutputEqual "( finally 'echo second'; echo 'test' )" "test\nsecond"
}

should_warn_about_deprecated_function() {
	deprecated_function() {
		deprecated "Place your text here"
	}
	assertOutputEqual 'deprecated_function 2>&1' "$0:24:function deprecated_function is deprecated: Place your text here"
}

should_warn_about_deprecated_script() {
	local tmpscript=$(mktemp)
	finally "rm -f '$tmpscript'"
	cat >"$tmpscript" <<EOF
. "$XDG_CONFIG_HOME/lib/utils.bash"
deprecated 'This whole script.'
EOF
	assertOutputEqual "bash $tmpscript 2>&1" "$tmpscript:2:script is deprecated: This whole script."
}

should_warn_about_deprecated_source_file() {
	local tmpscript=$(mktemp)
	local tmpsource=$(mktemp)
	finally "rm -f '$tmpscript' '$tmpsource' "
	cat >"$tmpsource" <<EOF
. "$XDG_CONFIG_HOME/lib/utils.bash"
deprecated 'This whole sourced file.'
EOF
	cat >"$tmpscript" <<EOF
. "$tmpsource"
EOF
	assertOutputEqual "bash $tmpscript 2>&1" "$tmpsource:2:script is deprecated: This whole sourced file."
}

unittest::run should_