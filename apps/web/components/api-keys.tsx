import { useMemo, useState } from "react";
import { toast } from "sonner";

import { ErrorAlert } from "@/components/error-alert";
import {
  useApiKeys,
  useCreateApiKey,
  useRevokeApiKey,
} from "@/hooks/use-api-keys";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Field, FieldDescription, FieldGroup, FieldLabel } from "./ui/field";
import { Input } from "./ui/input";

type ApiKeysProps = {
  projectId: string;
};

function formatDateTime(value: string | null) {
  if (!value) {
    return "Never used";
  }

  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

export function ApiKeys({ projectId }: ApiKeysProps) {
  const [apiKeyName, setApiKeyName] = useState("");
  const [createdRawKey, setCreatedRawKey] = useState<string | null>(null);
  const [createdApiKeyId, setCreatedApiKeyId] = useState<string | null>(null);
  const { data = [], isPending, error } = useApiKeys(projectId);
  const {
    mutate: createApiKey,
    isPending: isCreatingApiKey,
    error: createApiKeyError,
  } = useCreateApiKey(projectId, {
    onSuccess: (result) => {
      setApiKeyName("");
      setCreatedRawKey(result.raw_key);
      setCreatedApiKeyId(result.api_key.id);
      toast.success(`Created ${result.api_key.name}.`);
    },
  });
  const {
    mutate: revokeApiKey,
    isPending: isRevokingApiKey,
    error: revokeApiKeyError,
  } = useRevokeApiKey(projectId, {
    onSuccess: (result) => {
      toast.success(`Revoked ${result.name}.`);
    },
  });
  const sortedApiKeys = useMemo(() => {
    return [...data].sort((left, right) => {
      const leftIsRevoked = left.revoked_at !== null;
      const rightIsRevoked = right.revoked_at !== null;

      if (leftIsRevoked !== rightIsRevoked) {
        return leftIsRevoked ? 1 : -1;
      }

      return (
        new Date(right.created_at).getTime() - new Date(left.created_at).getTime()
      );
    });
  }, [data]);

  function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    createApiKey({
      name: apiKeyName.trim(),
    });
  }

  async function copyApiKey(apiKeyId: string, prefix: string) {
    if (createdRawKey && createdApiKeyId === apiKeyId) {
      await navigator.clipboard.writeText(createdRawKey);
      toast.success("API key copied.");
      return;
    }

    await navigator.clipboard.writeText(prefix);
    toast.message("Raw key unavailable", {
      description:
        "Only the key prefix is available now. Raw API keys are shown once when created.",
    });
  }

  function confirmAndRevokeApiKey(apiKeyId: string, apiKeyName: string) {
    const confirmed = window.confirm(
      `Revoke "${apiKeyName}"? This API key will stop working immediately.`
    );

    if (!confirmed) {
      return;
    }

    revokeApiKey(apiKeyId);
  }

  return (
    <section className="flex flex-col gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Create API key</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit}>
            <FieldGroup>
              {createApiKeyError ? (
                <ErrorAlert
                  title="Could not create API key"
                  description="Please try again. If the problem persists, check the API and try one more time."
                />
              ) : null}

              {revokeApiKeyError ? (
                <ErrorAlert
                  title="Could not revoke API key"
                  description="Please try again. If the problem persists, check the API and try one more time."
                />
              ) : null}

              {createdRawKey ? (
                <Card className="border-dashed">
                  <CardHeader>
                    <CardTitle className="text-base">
                      Copy this key now
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    <p className="text-sm text-muted-foreground">
                      This raw key is only shown once.
                    </p>
                    <code className="block overflow-x-auto border px-3 py-2 text-xs">
                      {createdRawKey}
                    </code>
                    <Button
                      type="button"
                      variant="outline"
                      className="cursor-pointer"
                      onClick={async () => {
                        await navigator.clipboard.writeText(createdRawKey);
                        toast.success("API key copied.");
                      }}
                    >
                      Copy key
                    </Button>
                  </CardContent>
                </Card>
              ) : null}

              <Field>
                <FieldLabel htmlFor="api-key-name">Key name</FieldLabel>
                <Input
                  id="api-key-name"
                  value={apiKeyName}
                  disabled={isCreatingApiKey}
                  placeholder="Production key"
                  onChange={(event) => setApiKeyName(event.target.value)}
                  required
                />
                <FieldDescription>
                  Give the key a name that makes its usage obvious later.
                </FieldDescription>
              </Field>

              <Field>
                <div className="flex gap-3">
                  <Button
                    type="submit"
                    disabled={isCreatingApiKey || apiKeyName.trim() === ""}
                    className="cursor-pointer"
                  >
                    {isCreatingApiKey ? "Creating..." : "Create API key"}
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    disabled={isCreatingApiKey || apiKeyName === ""}
                    className="cursor-pointer"
                    onClick={() => setApiKeyName("")}
                  >
                    Clear
                  </Button>
                </div>
              </Field>
            </FieldGroup>
          </form>
        </CardContent>
      </Card>

      {error ? (
        <ErrorAlert
          title="Could not load API keys"
          description="The dashboard could not fetch this project's API keys right now."
        />
      ) : null}

      {isPending && <p>Api keys loading...</p>}

      {sortedApiKeys.map((apiKey) => (
        <Card key={apiKey.id}>
          <CardHeader>
            <CardTitle>{apiKey.name}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            <p>Prefix: {apiKey.prefix}</p>
            <p>Created: {formatDateTime(apiKey.created_at)}</p>
            <p>Last used: {formatDateTime(apiKey.last_used_at)}</p>
            {apiKey.revoked_at ? (
              <p>Revoked: {formatDateTime(apiKey.revoked_at)}</p>
            ) : null}
            <div className="flex gap-3 pt-2">
              <Button
                type="button"
                variant="outline"
                className="cursor-pointer"
                onClick={() => copyApiKey(apiKey.id, apiKey.prefix)}
              >
                Copy key
              </Button>
              {!apiKey.revoked_at ? (
                <Button
                  type="button"
                  variant="destructive"
                  disabled={isRevokingApiKey}
                  className="cursor-pointer"
                  onClick={() => confirmAndRevokeApiKey(apiKey.id, apiKey.name)}
                >
                  {isRevokingApiKey ? "Revoking..." : "Delete key"}
                </Button>
              ) : null}
            </div>
          </CardContent>
        </Card>
      ))}

      {!isPending && !error && data.length === 0 && (
        <div className="gap-2 flex flex-col items-start p-2">
          <p className="pl-0.5">
            No api keys found, create one to start tracking events.
          </p>
        </div>
      )}
    </section>
  );
}
