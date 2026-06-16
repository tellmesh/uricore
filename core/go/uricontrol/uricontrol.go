package uricontrol

type Request struct {
	URI     string
	Payload map[string]any
	Context map[string]any
}

func DescribePlaceholder() string {
	return "uricontrol Go SDK placeholder"
}
